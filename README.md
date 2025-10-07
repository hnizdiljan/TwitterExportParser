# TwitterExportParser

Scraper and parser for Twitter/X.com data - scrapes user profiles and converts CSV exports to structured JSON format.

## Description

This project provides tools to work with Twitter/X.com data:
1. **X.com Scraper**: Directly scrape tweets from any public Twitter/X.com user profile with full thread support
2. **CSV Parser**: Convert CSV exports from TwExport Tools into structured JSON format

## Features

### X.com Scraper (undetected-chromedriver)
- **Two-phase scraping**: First collects all post URLs, then processes each one
- **Thread detection**: Automatically merges multi-part threads into single posts
- **Filters out**: Replies, Retweets, and quoted tweets (only original posts)
- **Anti-detection**: Uses undetected-chromedriver to avoid Twitter blocks
- **Full text extraction**: Opens each tweet to get complete text (not just preview)
- **Automatic login**: Uses credentials from config file
- **Progress tracking**: Shows detailed progress for both phases

### CSV Parser
- Parse Twitter CSV exports to Python dictionaries
- Convert CSV to formatted JSON files
- Extract tweet statistics (views, favorites, language distribution, etc.)
- Handle hashtags, URLs, and media attachments
- Support for multiple tweet types (Tweet, Reply, Retweet, Quoted)

## Installation

```bash
# Clone the repository
git clone https://github.com/hnizdiljan/TwitterExportParser.git
cd TwitterExportParser

# Install dependencies
pip install -r requirements.txt
```

## Requirements

- Python 3.7+
- undetected-chromedriver
- Chrome/Chromium browser installed

## Usage

### X.com Scraping (Recommended)

**Step 1: Setup Configuration File (First Time Only)**

1. Copy the example config file:
```bash
copy config.json.example config.json
```

2. Edit `config.json` with your Twitter credentials:
```json
{
  "twitter_credentials": {
    "email": "your_email@example.com",
    "password": "your_password",
    "username": "your_twitter_username"
  }
}
```

**Step 2: Scrape Posts**

```bash
# Scrape posts with full thread expansion (RECOMMENDED)
python scrape_tweets_undetected.py ankapirati output.json --login --limit 500

# Faster scraping without full text expansion (preview only)
python scrape_tweets_undetected.py ankapirati output.json --login --limit 500 --no-expand

# Custom config file
python scrape_tweets_undetected.py ankapirati output.json --login --config my_config.json --limit 500
```

**How it works:**
1. **Phase 1**: Scrolls through profile and collects URLs of all original posts (excludes replies and retweets)
2. **Phase 2**: Opens each post detail page to get full text and detect thread continuations
3. Automatically merges multi-part threads into single posts
4. Outputs sorted JSON with ID, text, type, and Author Username

### CSV to JSON Conversion

Convert existing CSV exports to JSON:

```bash
# Simple format (ID, text, type, Author Username only)
python convert.py Export_Twitter.csv output.json --simple

# Full format with all fields
python convert.py Export_Twitter.csv output.json

# With custom indentation
python convert.py Export_Twitter.csv output.json --indent 4

# Show statistics after conversion
python convert.py Export_Twitter.csv output.json --stats
```

### Python API

#### Scraping API

```python
import asyncio
from scraper import TwitterScraper

async def main():
    scraper = TwitterScraper()

    # Scrape tweets (simple format)
    tweets = await scraper.scrape_user_tweets_simple('ankapirati', limit=100)
    scraper.save_to_json(tweets, 'output.json')

    # Or full format
    tweets = await scraper.scrape_user_tweets('ankapirati', limit=100)
    scraper.save_to_json(tweets, 'output_full.json')

asyncio.run(main())
```

#### CSV Parser API

```python
from parser import TwitterCSVParser

# Initialize parser with your CSV file
parser = TwitterCSVParser('Export_Twitter.csv')

# Parse to list of dictionaries
tweets = parser.parse()

# Convert to JSON and save (simple format)
parser.to_json('output.json', simple=True)

# Get statistics
stats = parser.get_stats()
print(f"Total tweets: {stats['total_tweets']}")
print(f"Total views: {stats['total_views']}")
```

### Output JSON Structure

**Simple Format** (`--simple` flag):
```json
[
  {
    "ID": "1800448558702657834",
    "text": "Tweet text here...",
    "type": "Tweet",
    "Author Username": "ankapirati"
  }
]
```

**Full Format**:
```json
[
  {
    "ID": "1922943692773450087",
    "text": "Tweet text here...",
    "type": "Tweet",
    "Author Username": "ankapirati",
    "Author Name": "Ankapirátská Strana",
    "created_at": "2025-05-15T11:14:37+00:00",
    "language": "cs",
    "url": "https://x.com/ankapirati/status/1922943692773450087",
    "metrics": {
      "views": 189,
      "replies": 0,
      "retweets": 0,
      "quotes": 0,
      "favorites": 2,
      "bookmarks": 0
    },
    "hashtags": ["#Ankap", "#BTC"],
    "urls": ["https://example.com"],
    "media": {
      "photos": ["https://pbs.twimg.com/media/...jpg"],
      "videos": []
    }
  }
]
```

## API Reference

### TwitterUndetectedScraper

#### `login(email: str = None, password: str = None, username: str = None)`
Login to Twitter/X.com. Credentials can be passed directly or loaded from config.json.

#### `collect_post_urls(username: str, limit: int = 100, scroll_pause: float = 2.0) -> List[str]`
Phase 1: Collect URLs of all posts (not replies or retweets) from user profile.

#### `get_full_tweet_text(tweet_url: str, username: str) -> Dict[str, Any]`
Get full tweet text including thread continuation by opening tweet detail page.

#### `scrape_user_tweets_simple(username: str, limit: int = 100, scroll_pause: float = 2.0, expand_threads: bool = True) -> List[Dict[str, str]]`
Main scraping method. Returns list of posts with ID, text, type, and Author Username, sorted by ID ascending.

#### `save_to_json(data: List[Dict], output_file: str, indent: int = 2)`
Save scraped data to JSON file.

### TwitterCSVParser

#### `parse() -> List[Dict[str, Any]]`
Parse the CSV file and return a list of tweet dictionaries (full format).

#### `parse_simple() -> List[Dict[str, str]]`
Parse the CSV file and return simplified list (ID, text, type, Author Username) sorted by ID ascending.

#### `to_json(output_file_path: str = None, indent: int = 2, simple: bool = False) -> str`
Parse the CSV and convert to JSON format. Set `simple=True` for simplified output.

#### `get_stats() -> Dict[str, Any]`
Get statistics about the parsed tweets including:
- Total tweets count
- Language distribution
- Tweet type distribution
- Total and average views/favorites

## Important Notes

### Security
- **Credentials Storage**: Your Twitter credentials are stored in `config.json`. This file is NOT encrypted but is excluded from git.
- **Account Safety**: Use a dedicated Twitter account for scraping, not your main account.
- **DO NOT commit `config.json`**: The `.gitignore` file excludes it automatically.

### Scraping Best Practices
- **Login Required**: The scraper requires login for reliable access to tweets.
- **Anti-Detection**: Uses undetected-chromedriver to avoid Twitter's bot detection.
- **Thread Expansion**: Enable `expand_threads` (default) to get complete multi-part threads merged.
- **Rate Limiting**: Twitter may limit excessive scraping. Use reasonable limits (e.g., 500 posts).
- **Scroll Pause**: Adjust `--scroll-pause` if you have slow internet connection.

### Troubleshooting
- **Login Issues**: If login fails, Twitter may require verification. Browser will open automatically so you can see what's happening.
- **No Posts Found**: Check debug output to see if posts are being filtered out. May need to adjust filtering logic.
- **Session Errors**: Browser must stay open during scraping. Don't close it manually.
- **ChromeDriver Issues**: undetected-chromedriver manages ChromeDriver automatically. Ensure Chrome/Chromium is installed.

## License

This project is licensed under the MIT License.
