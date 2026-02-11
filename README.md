# Charlottesville Scrabble Event Generator

Natural language event row generator for Charlottesville Scrabble club events.
Created primarily by Claude Code / Claude Code for Web

## Features

- Natural language command interface powered by Claude AI
- Automatic date calculation for recurring events
- TSV format for easy copy-paste to Google Sheets
- Appends new events to bottom (preserves order, never edits existing rows)
- Template-based event generation
- Now available as a Claude Code skill (no setup required!)

## Using the Claude Code Skill (Recommended)

This project includes a Claude Code skill for easy event generation in Claude Code.

### Usage

Simply invoke the skill in Claude Code:

```
/add-scrabble-events add December 2026 club events
```

Or use natural language:

```
Can you add library events for January 2027?
```

The skill will automatically add rows to events.tsv.

### Example Commands

- "add December 2026 club events"
- "add library events for January 2027"
- "add 5th Friday for May 2026"
- "add club events and library events for February 2026"
- "add tournament on 3/15/26 called 'Spring Cup' at Walker Square"

## Event Patterns

The tool understands these recurring patterns:

### Club Events
- **Schedule**: 1st and 3rd Fridays of each month
- **Venue**: Wegmans 5th St
- **Time**: 5:30pm-8:30pm
- **Name**: Open gameplay

### 5th Friday Events
- **Schedule**: 5th Friday (only in months with 5 Fridays)
- **Venue**: Fuzzy's Tacos
- **Time**: 5:30pm-8:30pm
- **Name**: Open gameplay

### Library Events
- **Schedule**: 1st Wednesday of each month
- **Venue**: Central Library
- **Time**: 5:30pm-7pm
- **Name**: Scrabble at the Library

## Files

- `events.tsv` - Main event data file (copy-paste to Google Sheets)
- `.claude/skills/add-scrabble-events/` - Claude Code skill for event generation
- `archive/` - Legacy Python implementation (archived)

## Workflow

1. Run command to add events
2. Review the output to confirm events
3. Open `events.tsv` in a text editor
4. New events are always at the bottom (existing events never modified)
5. Copy all contents
6. Paste into your Google Sheet

## Customization

### Adding New Venues

Edit `.claude/skills/add-scrabble-events/references/event-rules.json` and add to the `venues` section:

```json
"new_venue": {
  "name": "Venue Name",
  "url": "https://google.maps/..."
}
```

### Adding New Event Patterns

Edit `.claude/skills/add-scrabble-events/references/event-rules.json` and add to the `event_patterns` section:

```json
"new_pattern": {
  "description": "Description for Claude",
  "schedule": "When it occurs",
  "template": {
    "name": "Event Name",
    "time": "Time range",
    "location": "Venue",
    "location_url": "URL",
    "info": "Info text",
    "info_url": "Info URL"
  }
}
```

## Examples of What You Can Say

With the Claude Code skill:

- "add rows for November's club events"
- "add December open gameplay sessions"
- "add all regular events for January 2027"
- "add tournament on 3/15/27 called 'Spring Championship' at Walker Square"
- "add 5th Friday events for May 2026"
- "add library events for the next 3 months"

Claude will interpret your command and generate the appropriate events!
