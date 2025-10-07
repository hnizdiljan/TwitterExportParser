import sys
import argparse
from pathlib import Path
from parser import TwitterCSVParser


def main():
    parser = argparse.ArgumentParser(
        description='Convert Twitter CSV export to JSON format',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python convert.py input.csv output.json
  python convert.py Export_Twitter.csv tweets.json --simple
  python convert.py input.csv output.json --indent 4
  python convert.py input.csv output.json --simple --stats
        '''
    )

    parser.add_argument(
        'input_csv',
        help='Path to input CSV file'
    )

    parser.add_argument(
        'output_json',
        help='Path to output JSON file'
    )

    parser.add_argument(
        '--indent',
        type=int,
        default=2,
        help='JSON indentation level (default: 2)'
    )

    parser.add_argument(
        '--simple',
        action='store_true',
        help='Output only ID, text, type, and Author Username fields (sorted by ID)'
    )

    parser.add_argument(
        '--stats',
        action='store_true',
        help='Display statistics after conversion'
    )

    args = parser.parse_args()

    # Check if input file exists
    input_path = Path(args.input_csv)
    if not input_path.exists():
        print(f"Error: Input file '{args.input_csv}' does not exist", file=sys.stderr)
        sys.exit(1)

    # Parse and convert
    try:
        print(f"Reading CSV file: {args.input_csv}")
        csv_parser = TwitterCSVParser(args.input_csv)

        print(f"Converting to JSON: {args.output_json}")
        csv_parser.to_json(args.output_json, indent=args.indent, simple=args.simple)

        if args.simple:
            print(f"✓ Successfully converted {args.input_csv} to {args.output_json} (simple format, sorted by ID)")
        else:
            print(f"✓ Successfully converted {args.input_csv} to {args.output_json}")

        # Display statistics if requested
        if args.stats:
            print("\n--- Statistics ---")
            stats = csv_parser.get_stats()
            print(f"Total tweets: {stats['total_tweets']}")
            print(f"Languages: {stats['languages']}")
            print(f"Tweet types: {stats['types']}")
            print(f"Total views: {stats['total_views']:,}")
            print(f"Total favorites: {stats['total_favorites']:,}")
            print(f"Average views per tweet: {stats['avg_views_per_tweet']:.2f}")
            print(f"Average favorites per tweet: {stats['avg_favorites_per_tweet']:.2f}")

    except Exception as e:
        print(f"Error during conversion: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
