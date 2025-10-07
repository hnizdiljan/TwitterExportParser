import csv
import json
from typing import List, Dict, Any
from pathlib import Path


class TwitterCSVParser:
    """Parser for CSV exports from TwExport Tools."""

    def __init__(self, csv_file_path: str):
        """
        Initialize the parser with a CSV file path.

        Args:
            csv_file_path: Path to the CSV file to parse
        """
        self.csv_file_path = Path(csv_file_path)

    def parse(self) -> List[Dict[str, Any]]:
        """
        Parse the CSV file and return a list of tweet dictionaries.

        Returns:
            List of dictionaries containing tweet data
        """
        tweets = []

        with open(self.csv_file_path, 'r', encoding='utf-8-sig') as csvfile:
            reader = csv.DictReader(csvfile)

            for row in reader:
                tweet = {
                    'id': row['ID'],
                    'text': row['Text'],
                    'language': row['Language'],
                    'type': row['Type'],
                    'author': {
                        'name': row['Author Name'],
                        'username': row['Author Username']
                    },
                    'metrics': {
                        'views': int(row['View Count']) if row['View Count'] else 0,
                        'replies': int(row['Reply Count']) if row['Reply Count'] else 0,
                        'retweets': int(row['Retweet Count']) if row['Retweet Count'] else 0,
                        'quotes': int(row['Quote Count']) if row['Quote Count'] else 0,
                        'favorites': int(row['Favorite Count']) if row['Favorite Count'] else 0,
                        'bookmarks': int(row['Bookmark Count']) if row['Bookmark Count'] else 0
                    },
                    'created_at': row['Created At'],
                    'url': row['Tweet URL'],
                    'source': row['Source'],
                    'hashtags': [tag.strip() for tag in row['hashtags'].split(',')] if row['hashtags'] else [],
                    'urls': [url.strip() for url in row['urls'].split(',')] if row['urls'] else [],
                    'media': {
                        'type': row['media_type'],
                        'urls': [url.strip() for url in row['media_urls'].split(',')] if row['media_urls'] else []
                    }
                }
                tweets.append(tweet)

        return tweets

    def parse_simple(self) -> List[Dict[str, str]]:
        """
        Parse the CSV file and return a simplified list with only essential fields.

        Returns:
            List of dictionaries containing only ID, text, type, and author username
        """
        tweets = []

        with open(self.csv_file_path, 'r', encoding='utf-8-sig') as csvfile:
            reader = csv.DictReader(csvfile)

            for row in reader:
                tweet = {
                    'ID': row['ID'],
                    'text': row['Text'],
                    'type': row['Type'],
                    'Author Username': row['Author Username']
                }
                tweets.append(tweet)

        # Sort by ID in ascending order
        tweets.sort(key=lambda x: int(x['ID']))

        return tweets

    def to_json(self, output_file_path: str = None, indent: int = 2, simple: bool = False) -> str:
        """
        Parse the CSV and convert to JSON format.

        Args:
            output_file_path: Optional path to save JSON output
            indent: Indentation level for JSON formatting
            simple: If True, output only ID, text, type, and Author Username (sorted by ID)

        Returns:
            JSON string representation of the tweets
        """
        if simple:
            tweets = self.parse_simple()
        else:
            tweets = self.parse()

        json_data = json.dumps(tweets, ensure_ascii=False, indent=indent)

        if output_file_path:
            with open(output_file_path, 'w', encoding='utf-8') as f:
                f.write(json_data)

        return json_data

    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the parsed tweets.

        Returns:
            Dictionary containing statistics
        """
        tweets = self.parse()

        total_tweets = len(tweets)
        languages = {}
        types = {}
        total_views = 0
        total_favorites = 0

        for tweet in tweets:
            lang = tweet['language']
            languages[lang] = languages.get(lang, 0) + 1

            tweet_type = tweet['type']
            types[tweet_type] = types.get(tweet_type, 0) + 1

            total_views += tweet['metrics']['views']
            total_favorites += tweet['metrics']['favorites']

        return {
            'total_tweets': total_tweets,
            'languages': languages,
            'types': types,
            'total_views': total_views,
            'total_favorites': total_favorites,
            'avg_views_per_tweet': total_views / total_tweets if total_tweets > 0 else 0,
            'avg_favorites_per_tweet': total_favorites / total_tweets if total_tweets > 0 else 0
        }
