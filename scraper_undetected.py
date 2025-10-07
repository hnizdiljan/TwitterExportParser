import json
import time
from typing import List, Dict, Any, Optional
from pathlib import Path
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException


class TwitterUndetectedScraper:
    """Scraper for Twitter/X.com using undetected-chromedriver (anti-detection)."""

    def __init__(self, headless: bool = False, config_path: str = "config.json"):
        """
        Initialize the undetected scraper.

        Args:
            headless: Run browser in headless mode (default: False, not recommended for login)
            config_path: Path to config file with credentials (default: config.json)
        """
        options = uc.ChromeOptions()

        if headless:
            options.add_argument('--headless=new')

        # Additional options
        options.add_argument('--start-maximized')
        options.add_argument('--disable-notifications')

        # Initialize undetected chrome
        self.driver = uc.Chrome(options=options, version_main=None)
        self.wait = WebDriverWait(self.driver, 20)
        self.logged_in = False
        self.config_path = config_path

    def load_credentials(self) -> Optional[Dict[str, str]]:
        """
        Load Twitter credentials from config file.

        Returns:
            Dictionary with email, password, username or None if file doesn't exist
        """
        if not Path(self.config_path).exists():
            return None

        with open(self.config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            return config.get('twitter_credentials')

    def login(self, email: str = None, password: str = None, username: str = None):
        """
        Login to Twitter/X.com.

        Args:
            email: Twitter email (optional if using config file)
            password: Twitter password (optional if using config file)
            username: Twitter username (optional if using config file)
        """
        # Try to load from config if credentials not provided
        if not email or not password:
            credentials = self.load_credentials()
            if credentials:
                email = email or credentials.get('email')
                password = password or credentials.get('password')
                username = username or credentials.get('username')
            else:
                raise ValueError("No credentials provided and config.json not found")

        print("Logging in to X.com...")
        self.driver.get("https://x.com/i/flow/login")
        time.sleep(4)

        try:
            # Enter email/username
            print("  Entering email/username...")
            email_input = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'input[autocomplete="username"]'))
            )
            # Simulate human typing
            for char in email:
                email_input.send_keys(char)
                time.sleep(0.1)
            time.sleep(2)

            # Click "Next" button
            print("  Clicking Next button...")
            next_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, '//button[.//span[contains(text(), "Next")] or .//span[contains(text(), "Další")]]'))
            )
            next_button.click()
            time.sleep(4)

            # Check for username verification
            print("  Checking for username verification...")
            try:
                username_input = self.driver.find_element(By.CSS_SELECTOR, 'input[data-testid="ocfEnterTextTextInput"]')
                if username_input.is_displayed() and username:
                    print("  Username verification required, entering username...")
                    for char in username:
                        username_input.send_keys(char)
                        time.sleep(0.1)
                    time.sleep(2)

                    # Click Next
                    next_button = self.driver.find_element(By.XPATH, '//button[.//span[contains(text(), "Next")] or .//span[contains(text(), "Další")]]')
                    next_button.click()
                    time.sleep(4)
            except (NoSuchElementException, TimeoutException):
                print("  No username verification needed")

            # Enter password
            print("  Entering password...")
            password_input = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="password"]'))
            )
            # Simulate human typing
            for char in password:
                password_input.send_keys(char)
                time.sleep(0.1)
            time.sleep(2)

            # Click "Log in" button
            print("  Clicking Log in button...")
            login_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, '//button[.//span[contains(text(), "Log in")] or .//span[contains(text(), "Přihlásit")]]'))
            )
            login_button.click()
            time.sleep(6)

            # Verify login
            print("  Verifying login...")
            try:
                self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="AppTabBar_Home_Link"]')))
                print("✓ Successfully logged in to X.com")
                self.logged_in = True
            except TimeoutException:
                if "home" in self.driver.current_url:
                    print("✓ Successfully logged in to X.com (verified by URL)")
                    self.logged_in = True
                else:
                    print(f"⚠ Warning: Could not verify login (URL: {self.driver.current_url})")
                    self.driver.save_screenshot("login_verification_error.png")
                    self.logged_in = True

        except Exception as e:
            print(f"\n  ERROR Details:")
            print(f"  Current URL: {self.driver.current_url}")
            self.driver.save_screenshot("login_failed.png")
            print(f"  Screenshot saved to login_failed.png")
            raise Exception(f"Login failed: {str(e)}")

    def get_full_tweet_text(self, tweet_url: str, username: str) -> Dict[str, Any]:
        """
        Get full tweet text including thread continuation by opening tweet detail page.

        Args:
            tweet_url: Full URL to the tweet
            username: Username of the account we're scraping

        Returns:
            Dictionary with full text and thread info
        """
        print(f"\n  Opening tweet detail: {tweet_url}")

        # Save current URL
        current_url = self.driver.current_url

        full_text_parts = []
        thread_ids = []

        try:
            # Navigate to tweet detail
            self.driver.get(tweet_url)
            time.sleep(3)

            # Find all articles on the page
            articles = self.driver.find_elements(By.CSS_SELECTOR, 'article[data-testid="tweet"]')

            for article in articles:
                try:
                    # Check if this tweet is from our target user
                    user_link = article.find_element(By.CSS_SELECTOR, f'a[href="/{username}"]')

                    # Get tweet ID
                    tweet_link = article.find_element(By.CSS_SELECTOR, 'a[href*="/status/"]')
                    tweet_href = tweet_link.get_attribute('href')
                    tweet_id = tweet_href.split('/status/')[-1].split('?')[0] if '/status/' in tweet_href else None

                    if tweet_id:
                        thread_ids.append(tweet_id)

                    # Get tweet text
                    try:
                        text_elem = article.find_element(By.CSS_SELECTOR, '[data-testid="tweetText"]')
                        text = text_elem.text
                        if text and text not in full_text_parts:
                            full_text_parts.append(text)
                    except NoSuchElementException:
                        pass

                except NoSuchElementException:
                    # This tweet is not from our user, skip
                    continue

            # Scroll down to load replies
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)

            # Check replies for thread continuation
            articles = self.driver.find_elements(By.CSS_SELECTOR, 'article[data-testid="tweet"]')

            for article in articles:
                try:
                    # Check if this tweet is from our target user
                    user_link = article.find_element(By.CSS_SELECTOR, f'a[href="/{username}"]')

                    # Get tweet ID
                    tweet_link = article.find_element(By.CSS_SELECTOR, 'a[href*="/status/"]')
                    tweet_href = tweet_link.get_attribute('href')
                    tweet_id = tweet_href.split('/status/')[-1].split('?')[0] if '/status/' in tweet_href else None

                    if tweet_id and tweet_id not in thread_ids:
                        thread_ids.append(tweet_id)

                        # Get tweet text
                        try:
                            text_elem = article.find_element(By.CSS_SELECTOR, '[data-testid="tweetText"]')
                            text = text_elem.text
                            if text and text not in full_text_parts:
                                full_text_parts.append(text)
                        except NoSuchElementException:
                            pass

                except NoSuchElementException:
                    continue

        except Exception as e:
            print(f"    Error getting full text: {str(e)}")
        finally:
            # Go back to original URL
            self.driver.get(current_url)
            time.sleep(2)

        # Combine all parts with newlines
        full_text = "\n".join(full_text_parts)

        return {
            'full_text': full_text,
            'thread_ids': thread_ids,
            'is_thread': len(thread_ids) > 1
        }

    def collect_post_urls(self, username: str, limit: int = 100, scroll_pause: float = 2.0) -> List[str]:
        """
        Collect URLs of all posts (not replies or retweets) from user profile.

        Args:
            username: Twitter username (without @)
            limit: Maximum number of posts to collect
            scroll_pause: Pause time between scrolls in seconds

        Returns:
            List of post URLs
        """
        # Go to Posts tab specifically
        url = f"https://x.com/{username}"
        print(f"\n📋 Phase 1: Collecting post URLs from {url}...")

        self.driver.get(url)
        time.sleep(5)

        post_urls = []
        seen_ids = set()
        scroll_attempts = 0
        max_scroll_attempts = 100
        no_new_posts_count = 0

        print(f"  Debug: Starting to collect posts...")

        while len(post_urls) < limit and scroll_attempts < max_scroll_attempts:
            previous_count = len(post_urls)

            # Find all tweet articles
            tweet_elements = self.driver.find_elements(By.CSS_SELECTOR, 'article[data-testid="tweet"]')
            print(f"  Debug: Found {len(tweet_elements)} tweet elements on page")

            for tweet_elem in tweet_elements:
                if len(post_urls) >= limit:
                    break

                try:
                    # Extract tweet ID from link first
                    tweet_link = tweet_elem.find_element(By.CSS_SELECTOR, 'a[href*="/status/"]')
                    tweet_url = tweet_link.get_attribute('href')
                    tweet_id = tweet_url.split('/status/')[-1].split('?')[0] if '/status/' in tweet_url else None

                    if not tweet_id or tweet_id in seen_ids:
                        continue

                    # Check if the tweet is from our target user
                    is_from_target_user = False
                    try:
                        # Look for the username link in the tweet
                        user_links = tweet_elem.find_elements(By.CSS_SELECTOR, 'a[href*="/' + username + '"]')
                        for link in user_links:
                            # Check if this is the author link (not a mention or quoted tweet)
                            href = link.get_attribute('href')
                            if href == f"https://x.com/{username}" or href == f"https://twitter.com/{username}":
                                # This is likely the author
                                is_from_target_user = True
                                break
                    except:
                        pass

                    if not is_from_target_user:
                        print(f"  Debug: Skipping {tweet_id} - not from target user")
                        continue

                    # Check if this is a retweet or reply (skip them)
                    is_retweet_or_reply = False
                    try:
                        social_context = tweet_elem.find_elements(By.CSS_SELECTOR, '[data-testid="socialContext"]')
                        if social_context and len(social_context) > 0:
                            context_text = social_context[0].text.lower()
                            print(f"  Debug: Social context for {tweet_id}: {context_text[:50]}")
                            if "retweeted" in context_text or "reposted" in context_text or "replied" in context_text:
                                is_retweet_or_reply = True
                                print(f"  Debug: Skipping {tweet_id} - is retweet/reply")
                    except Exception as e:
                        pass

                    if is_retweet_or_reply:
                        continue

                    # This is a valid post!
                    seen_ids.add(tweet_id)
                    post_urls.append(tweet_url)
                    print(f"  Collected {len(post_urls)}/{limit} post URLs... (latest: {tweet_id})")

                except Exception as e:
                    print(f"  Debug: Error processing tweet: {str(e)}")
                    continue

            # Check if we found new posts
            if len(post_urls) == previous_count:
                no_new_posts_count += 1
                print(f"  Debug: No new posts in this scroll ({no_new_posts_count}/5)")
                if no_new_posts_count >= 5:
                    print(f"\n  No new posts found after 5 scrolls, stopping collection...")
                    break
            else:
                no_new_posts_count = 0

            # Scroll down to load more tweets
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(scroll_pause)
            scroll_attempts += 1

        print(f"\n✓ Collected {len(post_urls)} post URLs")
        return post_urls

    def scrape_user_tweets_simple(self, username: str, limit: int = 100, scroll_pause: float = 2.0, expand_threads: bool = True) -> List[Dict[str, str]]:
        """
        Scrape tweets from a user profile (simple format).

        Args:
            username: Twitter username (without @)
            limit: Maximum number of tweets to scrape
            scroll_pause: Pause time between scrolls in seconds
            expand_threads: If True, open each tweet to get full text and threads

        Returns:
            List of dictionaries with ID, text, type, and Author Username
        """
        # Phase 1: Collect all post URLs
        post_urls = self.collect_post_urls(username, limit, scroll_pause)

        if not post_urls:
            print("⚠ No posts found!")
            return []

        # Phase 2: Get full text for each post
        print(f"\n📝 Phase 2: Getting full text for {len(post_urls)} posts...")
        tweets = []
        processed_thread_ids = set()

        for i, post_url in enumerate(post_urls, 1):
            try:
                # Extract tweet ID
                tweet_id = post_url.split('/status/')[-1].split('?')[0]

                # Skip if already processed as part of a thread
                if tweet_id in processed_thread_ids:
                    print(f"  [{i}/{len(post_urls)}] Skipping {tweet_id} (already processed in thread)")
                    continue

                print(f"  [{i}/{len(post_urls)}] Processing post {tweet_id}...", end='')

                if expand_threads:
                    # Get full text with thread detection
                    full_tweet_data = self.get_full_tweet_text(post_url, username)
                    text = full_tweet_data['full_text']

                    # Mark all thread IDs as processed
                    for thread_id in full_tweet_data['thread_ids']:
                        processed_thread_ids.add(thread_id)

                    print(f" ✓ ({len(full_tweet_data['thread_ids'])} part{'s' if len(full_tweet_data['thread_ids']) > 1 else ''})")
                else:
                    # Just navigate and get basic text
                    self.driver.get(post_url)
                    time.sleep(2)

                    try:
                        article = self.driver.find_element(By.CSS_SELECTOR, 'article[data-testid="tweet"]')
                        text_elem = article.find_element(By.CSS_SELECTOR, '[data-testid="tweetText"]')
                        text = text_elem.text
                    except NoSuchElementException:
                        text = ""

                    print(f" ✓")

                tweet_dict = {
                    'ID': tweet_id,
                    'text': text,
                    'type': 'Tweet',
                    'Author Username': username
                }

                tweets.append(tweet_dict)

            except Exception as e:
                print(f" ✗ Error: {str(e)}")
                continue

        print(f"\n✓ Scraped {len(tweets)} posts from @{username}")

        # Sort by ID ascending
        tweets.sort(key=lambda x: int(x['ID']))

        return tweets

    def save_to_json(self, data: List[Dict[str, Any]], output_file: str, indent: int = 2):
        """Save scraped data to JSON file."""
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=indent)
        print(f"✓ Saved to {output_file}")

    def close(self):
        """Close the browser."""
        self.driver.quit()
