import sys
import argparse
from scraper_undetected import TwitterUndetectedScraper


def main():
    parser = argparse.ArgumentParser(
        description='Scrape tweets from X.com using undetected-chromedriver (BEST for login)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python scrape_tweets_undetected.py ankapirati output.json --login
  python scrape_tweets_undetected.py ankapirati output.json --limit 500 --login
  python scrape_tweets_undetected.py ankapirati output.json --login --config my_config.json

Setup:
  1. Copy config.json.example to config.json
  2. Edit config.json with your Twitter credentials
  3. Run with --login flag to use credentials

Note: This scraper uses undetected-chromedriver which is harder to detect.
Headless mode is NOT recommended for login (Twitter may block it).
        '''
    )

    parser.add_argument(
        'username',
        help='Twitter username to scrape (without @)'
    )

    parser.add_argument(
        'output_json',
        help='Path to output JSON file'
    )

    parser.add_argument(
        '--limit',
        type=int,
        default=100,
        help='Maximum number of tweets to scrape (default: 100)'
    )

    parser.add_argument(
        '--login',
        action='store_true',
        help='Login to Twitter before scraping (uses config.json)'
    )

    parser.add_argument(
        '--config',
        type=str,
        default='config.json',
        help='Path to config file with credentials (default: config.json)'
    )

    parser.add_argument(
        '--headless',
        action='store_true',
        help='Run browser in headless mode (NOT recommended for login!)'
    )

    parser.add_argument(
        '--indent',
        type=int,
        default=2,
        help='JSON indentation level (default: 2)'
    )

    parser.add_argument(
        '--scroll-pause',
        type=float,
        default=2.0,
        help='Pause time between scrolls in seconds (default: 2.0)'
    )

    parser.add_argument(
        '--no-expand',
        action='store_true',
        help='Do not expand tweets to get full text and threads (faster but less complete)'
    )

    args = parser.parse_args()

    if args.login and args.headless:
        print("⚠ Warning: Headless mode with login is not recommended and may fail!")
        print("  Twitter often blocks headless browsers during login.")
        response = input("  Continue anyway? (y/n): ")
        if response.lower() != 'y':
            print("Exiting...")
            sys.exit(0)

    scraper = None
    try:
        print(f"Initializing undetected-chromedriver scraper...")
        scraper = TwitterUndetectedScraper(headless=args.headless, config_path=args.config)

        # Login if requested
        if args.login:
            scraper.login()

        # Scrape tweets
        expand_threads = not args.no_expand
        if expand_threads:
            print("\n📝 Full text expansion enabled - each tweet will be opened to get complete text and threads")
            print("   This is slower but more complete. Use --no-expand for faster scraping.\n")

        tweets = scraper.scrape_user_tweets_simple(
            args.username,
            limit=args.limit,
            scroll_pause=args.scroll_pause,
            expand_threads=expand_threads
        )

        # Save to JSON
        scraper.save_to_json(tweets, args.output_json, indent=args.indent)

        print(f"\n✓ Successfully scraped {len(tweets)} tweets from @{args.username}")

    except Exception as e:
        print(f"\nError during scraping: {str(e)}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        if scraper:
            print("\nClosing browser...")
            scraper.close()


if __name__ == '__main__':
    main()
