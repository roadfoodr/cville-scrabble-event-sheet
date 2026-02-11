#!/usr/bin/env python3
"""
Calculate event dates for recurring Scrabble event patterns.
Returns dates in M/D/YY format as JSON array.
"""

import argparse
import json
import sys
from calendar import monthrange
from datetime import date


def get_nth_weekday(year: int, month: int, weekday: int, n: int) -> date | None:
    """
    Get the nth occurrence of a weekday in a given month.

    Args:
        year: Year (e.g., 2026)
        month: Month (1-12)
        weekday: Day of week (0=Monday, 4=Friday, 2=Wednesday)
        n: Which occurrence (1=first, 3=third, 5=fifth)

    Returns:
        date object or None if the nth occurrence doesn't exist
    """
    # Get first day of month and total days
    first_day = date(year, month, 1)
    days_in_month = monthrange(year, month)[1]

    # Find first occurrence of the weekday
    first_weekday_of_month = first_day.weekday()
    days_until_target = (weekday - first_weekday_of_month) % 7
    first_occurrence = 1 + days_until_target

    # Calculate nth occurrence
    target_day = first_occurrence + (n - 1) * 7

    # Return None if it's beyond the month
    if target_day > days_in_month:
        return None

    return date(year, month, target_day)


def format_date(d: date) -> str:
    """Format date as M/D/YY"""
    return f"{d.month}/{d.day}/{d.year % 100}"


def calculate_club_events(year: int, month: int) -> list[str]:
    """
    Calculate club event dates (1st and 3rd Friday).

    Returns:
        List of date strings in M/D/YY format
    """
    dates = []

    # 1st Friday
    first_friday = get_nth_weekday(year, month, 4, 1)  # 4 = Friday
    if first_friday:
        dates.append(format_date(first_friday))

    # 3rd Friday
    third_friday = get_nth_weekday(year, month, 4, 3)
    if third_friday:
        dates.append(format_date(third_friday))

    return dates


def calculate_library_events(year: int, month: int) -> list[str]:
    """
    Calculate library event dates (1st Wednesday).

    Returns:
        List of date strings in M/D/YY format
    """
    dates = []

    # 1st Wednesday
    first_wednesday = get_nth_weekday(year, month, 2, 1)  # 2 = Wednesday
    if first_wednesday:
        dates.append(format_date(first_wednesday))

    return dates


def calculate_fifth_friday(year: int, month: int) -> list[str]:
    """
    Calculate 5th Friday if it exists in the month.

    Returns:
        List of date strings in M/D/YY format (empty if no 5th Friday)
    """
    dates = []

    # 5th Friday
    fifth_friday = get_nth_weekday(year, month, 4, 5)  # 4 = Friday
    if fifth_friday:
        dates.append(format_date(fifth_friday))

    return dates


def main():
    parser = argparse.ArgumentParser(
        description='Calculate event dates for recurring Scrabble event patterns'
    )
    parser.add_argument(
        '--pattern',
        required=True,
        choices=['club_events', 'library_events', 'fifth_friday'],
        help='Event pattern type'
    )
    parser.add_argument(
        '--month',
        type=int,
        required=True,
        help='Month (1-12)'
    )
    parser.add_argument(
        '--year',
        type=int,
        required=True,
        help='Year (e.g., 2026)'
    )

    args = parser.parse_args()

    # Validate month
    if not 1 <= args.month <= 12:
        print(f"Error: Month must be between 1 and 12, got {args.month}", file=sys.stderr)
        sys.exit(1)

    # Calculate dates based on pattern
    if args.pattern == 'club_events':
        dates = calculate_club_events(args.year, args.month)
    elif args.pattern == 'library_events':
        dates = calculate_library_events(args.year, args.month)
    elif args.pattern == 'fifth_friday':
        dates = calculate_fifth_friday(args.year, args.month)
    else:
        print(f"Error: Unknown pattern '{args.pattern}'", file=sys.stderr)
        sys.exit(1)

    # Output as JSON array
    print(json.dumps(dates))


if __name__ == '__main__':
    main()
