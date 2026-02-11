---
name: add-scrabble-events
description: Generate Scrabble event rows for events.tsv from natural language commands. Use when the user requests adding events to the schedule, such as "add December's club events", "add library events for January", "add 5th Friday events", or "add tournament on 3/15/26". Interprets event types (club_events, library_events, fifth_friday, custom tournaments), calculates recurring dates (1st/3rd Fridays, 1st Wednesdays), and appends properly formatted TSV rows to events.tsv.
---

# Add Scrabble Events

Generate event rows for the Charlottesville Scrabble club schedule from natural language commands.

## Overview

This skill appends new event rows to `events.tsv` in the project root. Each row contains 7 tab-delimited columns:

```
Date    Name    Time    Location    location_URL    Info    info_url
```

Date format: `M/D/YY` (e.g., "12/4/26")

## Process

1. Read `references/event-rules.json` for event patterns and venues
2. Read existing `events.tsv` to understand current events
3. Parse the user's command to identify:
   - Event type(s): `club_events`, `library_events`, `fifth_friday`, or custom
   - Time period: specific month(s), date range, or single date
4. **Validate venue against references**: If the user mentions a venue or location:
   - Check if it matches any venue in `references/event-rules.json` under the `venues` section
   - Common venue names to look for: "Wegmans", "Walker Square", "Jefferson School", "Central Library", "Fuzzy's", "Dairy Market", "Scrabble Schoolhouse"
   - If a match is found, use the standardized `name` and `url` from the references
   - If no match is found, use the venue name/address as provided and create an appropriate Google Maps URL
5. Calculate specific dates using the date calculation script
6. Generate event objects from templates in event-rules.json
7. Append new TSV rows to events.tsv (never modify existing rows)
8. **Verify the append operation**:
   - After appending new rows, read the last few lines of events.tsv to confirm successful write
   - Verify proper line separation (no concatenation onto previous line)
   - Verify tab delimiting is correct
9. Display summary of added events

**Important**: Use AskUserQuestion to request clarifications whenever information is missing or ambiguous. Don't make assumptions about event details, venues, dates, or registration URLs.

## Event Patterns

Three recurring patterns are defined in `references/event-rules.json`:

- **club_events**: 1st and 3rd Friday of the month at Wegmans 5th St (5:30pm-8:30pm)
- **library_events**: 1st Wednesday of the month at Central Library (5:30pm-7pm)
- **fifth_friday**: 5th Friday of the month at Fuzzy's Tacos (5:30pm-8:30pm) - only in applicable months

For custom tournaments or one-off events, extract details from the user's command.

## Custom Tournament Event Process

When adding a custom tournament (not a recurring pattern), follow this process:

1. **Extract basic information** from user's command:
   - Event name/title
   - Date (specific date, not a recurring pattern)
   - Time range
   - Venue/location mentioned

2. **Validate and standardize venue**:
   - Check venue against `references/event-rules.json` venues list
   - Use standardized venue name and URL if match found
   - For addresses like "100 Wegmans Wy" → use "Wegmans 5th St"

3. **Request clarifications** if any information is missing or unclear:
   - Use AskUserQuestion for any missing required fields (date, venue, time)
   - Ask for registration URL (info_url) if not provided
   - Clarify any ambiguous venue names or event details
   - Example: "Do you have a registration URL (like a Google Doc or website) for this event?"

4. **Format the event**:
   - Name: Prefix with "Tournament - " if not already present
   - Time: Simple range format (e.g., "11am-5:30pm")
   - Location: Use standardized venue name from references
   - location_URL: Use standardized URL from references
   - Info: Use "details and registration" (standard for all tournaments)
   - info_url: Registration URL provided by user (or empty if none)

5. **Append to events.tsv** using reliable method (see File Operations below)

6. **Verify the write operation**:
   - After appending, read the last few lines of events.tsv using Read tool or `tail` command
   - Confirm the new event row(s) appear on separate lines with proper tab delimiting
   - Display the added events to the user with a summary

**General Guidance**: Throughout this process, use AskUserQuestion whenever you need clarifications or additional information. Don't make assumptions about missing details.

## Date Calculation

Use `scripts/calculate_dates.py` for reliable date calculations:

```bash
python .claude/skills/add-scrabble-events/scripts/calculate_dates.py --pattern <pattern> --month <M> --year <YYYY>
```

Examples:
```bash
# Club events for December 2026
python .claude/skills/add-scrabble-events/scripts/calculate_dates.py --pattern club_events --month 12 --year 2026
# Returns: ["12/4/26", "12/18/26"]

# Library events for January 2027
python .claude/skills/add-scrabble-events/scripts/calculate_dates.py --pattern library_events --month 1 --year 2027
# Returns: ["1/7/27"]

# 5th Friday for May 2026
python .claude/skills/add-scrabble-events/scripts/calculate_dates.py --pattern fifth_friday --month 5 --year 2026
# Returns: ["5/29/26"] or [] if no 5th Friday exists
```

The script returns a JSON array of dates in M/D/YY format.

## Template Application

Templates are stored in `references/event-rules.json` under `event_patterns.<pattern>.template`.

Each template contains:
- `name`: Event name
- `time`: Time range (e.g., "5:30pm-8:30pm")
- `location`: Venue name
- `location_url`: Google Maps URL
- `info`: Additional information (may contain `{nth}` placeholder)
- `info_url`: Optional URL

For the `{nth}` placeholder in the info field:
- Use "1st" for 1st Friday/Wednesday
- Use "3rd" for 3rd Friday
- Use "5th" for 5th Friday

### Info Field Conventions

Different event types use different Info field formats:

- **Recurring club events**: Use `{nth}` placeholder → "1st Friday", "3rd Friday", "5th Friday"
- **Library events**: "presented with JMRL"
- **All tournament events**: "details and registration"
- **Special one-off events**: May use custom text as appropriate

For consistency, **always use "details and registration"** for tournament events, regardless of entry fee, number of games, or other details. Specific event details should be in the registration document linked via info_url.

Venue information is also available in `references/event-rules.json` under `venues` if needed for custom events.

## TSV Format Requirements

- **Column order**: Date, Name, Time, Location, location_URL, Info, info_url (exactly 7 columns)
- **Delimiter**: Tab character (not spaces)
- **Date format**: M/D/YY (e.g., "12/4/26", not "12/04/2026")
- **Empty fields**: Use empty string, not null or "N/A"
- **Preserve formatting**: Never modify or reorder existing rows
- **Append only**: Always add new rows at the bottom

## File Operations

### Appending Events to TSV

**Important**: Do not use `echo >> file` for appending, as this can fail if the file lacks a trailing newline.

**Recommended approach**:
1. Read the current events.tsv file using the Read tool
2. Use the Edit tool to append the new row(s)
3. This ensures proper line breaks and tab formatting

**Alternative approach** (if using Bash):
- Verify the file ends with a newline before appending
- Use `printf` instead of `echo` for more reliable formatting
- Example: `printf "%s\n" "date\tname\ttime..." >> events.tsv`

## Validation and Safety

Before appending events:

1. Check for duplicates: Same date + name combination already exists
2. Validate date format: Must be M/D/YY
3. Ensure all required fields are present (Date, Name, Time, Location)
4. Never modify existing rows
5. Always append new rows at the bottom

If duplicates are detected, warn the user and skip those events.

## Example Commands

```
add December 2026 club events
add library events for January 2027
add 5th Friday for May 2026
add club events and library events for February 2026
add tournament on 3/15/26 called 'Spring Cup' at Walker Square
add Commonwealth Cup on 4/10/26 at Jefferson School from 10am-4pm
```

## Output Summary

After adding events, display a user-friendly summary:

```
Added 2 events to events.tsv:
- 12/4/26 - Open gameplay at Wegmans 5th St (1st Friday)
- 12/18/26 - Open gameplay at Wegmans 5th St (3rd Friday)
```

Include the date, name, location, and any distinguishing info (like "1st Friday", "5th Friday", etc.) for each event.
