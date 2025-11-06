#!/usr/bin/env python3
"""
Natural language event row generator for Charlottesville Scrabble club.
Uses Anthropic's Claude API to parse commands and generate event rows.
"""

import csv
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

import anthropic
from dateutil.parser import parse as parse_date
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# File paths
SCRIPT_DIR = Path(__file__).parent
EVENTS_FILE = SCRIPT_DIR / "events.tsv"
RULES_FILE = SCRIPT_DIR / "rules.json"


def load_rules() -> Dict[str, Any]:
    """Load event patterns and templates from rules.json"""
    with open(RULES_FILE, 'r') as f:
        return json.load(f)


def load_events() -> List[Dict[str, str]]:
    """Load existing events from TSV file"""
    if not EVENTS_FILE.exists():
        return []

    with open(EVENTS_FILE, 'r', newline='') as f:
        reader = csv.DictReader(f, delimiter='\t')
        return list(reader)


def save_events(events: List[Dict[str, str]]) -> None:
    """Save events back to TSV file, sorted by date"""
    # Sort by date
    def parse_event_date(date_str: str) -> datetime:
        """Parse date from M/D/YY format"""
        try:
            parts = date_str.split('/')
            month, day, year = int(parts[0]), int(parts[1]), int(parts[2])
            # Assume 20XX for years
            full_year = 2000 + year
            return datetime(full_year, month, day)
        except:
            return datetime.min

    events.sort(key=lambda e: parse_event_date(e['Date']))

    # Write to file
    fieldnames = ['Date', 'Name', 'Time', 'Location', 'location_URL', 'Info', 'info_url']
    with open(EVENTS_FILE, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter='\t')
        writer.writeheader()
        writer.writerows(events)


def parse_command_with_llm(command: str, rules: Dict[str, Any]) -> Dict[str, Any]:
    """Use Anthropic API to parse the natural language command"""
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        raise ValueError(
            'ANTHROPIC_API_KEY environment variable not set. '
            'Please set it to use this tool.'
        )

    client = anthropic.Anthropic(api_key=api_key)

    system_prompt = f"""You are an event generation assistant for a Scrabble club. Your job is to interpret natural language commands and generate structured event data.

Here are the event patterns and templates available:
{json.dumps(rules, indent=2)}

Current date context: Today is November 6, 2024.

When given a command, you should:
1. Identify which event pattern(s) are being requested
2. Determine the date(s) for the events
3. Return a JSON array of events to be added

Each event should have this structure:
{{
  "Date": "M/D/YY",
  "Name": "event name",
  "Time": "time range",
  "Location": "venue name",
  "location_URL": "google maps url",
  "Info": "additional info",
  "info_url": "optional url"
}}

For recurring events:
- "club events" = 1st and 3rd Friday open gameplay at Wegmans
- "5th Friday" = 5th Friday events at Fuzzy's Tacos (only months with 5 Fridays)
- "library events" = 1st Wednesday at Central Library

Rules for dates:
- 1st Friday = first Friday of the month
- 3rd Friday = third Friday of the month
- 5th Friday = fifth Friday (only in months that have 5 Fridays)
- 1st Wednesday = first Wednesday of the month

Return ONLY a valid JSON object with this structure:
{{
  "events": [array of event objects],
  "explanation": "brief explanation of what was added"
}}"""

    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=4096,
        system=system_prompt,
        messages=[{
            "role": "user",
            "content": command
        }]
    )

    response_text = response.content[0].text

    # Try to parse JSON from response
    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        # Try to extract JSON if it's wrapped in markdown
        import re
        json_match = re.search(r'```(?:json)?\n(.*?)\n```', response_text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(1))
        raise ValueError(f'Failed to parse LLM response as JSON: {response_text}')


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print('Usage: python generate.py "<command>"')
        print('Example: python generate.py "add rows for November\'s club events"')
        print('\nOr with uv:')
        print('Usage: uv run generate.py "<command>"')
        sys.exit(1)

    command = ' '.join(sys.argv[1:])

    print(f'Processing command: "{command}"\n')

    try:
        # Load data
        rules = load_rules()
        existing_events = load_events()

        # Parse command with LLM
        print('Interpreting command with AI...')
        result = parse_command_with_llm(command, rules)

        if not result.get('events') or len(result['events']) == 0:
            print('No events to add.')
            return

        print(f"\n{result.get('explanation', '')}\n")
        print(f"Adding {len(result['events'])} event(s):\n")

        # Display events to be added
        for idx, event in enumerate(result['events'], 1):
            print(f"{idx}. {event['Date']} - {event['Name']} at {event['Location']}")

        # Add new events
        all_events = existing_events + result['events']

        # Save back to file
        save_events(all_events)

        print(f"\n✓ Successfully added {len(result['events'])} event(s) to {EVENTS_FILE}")
        print('You can now copy-paste the contents into your Google Sheet.')

    except Exception as error:
        print(f'Error: {error}', file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
