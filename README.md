# Charlottesville Scrabble Event Generator

Natural language event row generator for Charlottesville Scrabble club events.

## Features

- 🤖 Natural language command interface powered by Claude AI
- 📅 Automatic date calculation for recurring events
- 📋 TSV format for easy copy-paste to Google Sheets
- 🔄 Auto-sorts events by date
- 📝 Template-based event generation

## Setup

### 1. Install Dependencies

```bash
npm install
```

### 2. Set API Key

You need an Anthropic API key to use this tool:

```bash
export ANTHROPIC_API_KEY="your-api-key-here"
```

Or add it to your shell profile (.bashrc, .zshrc, etc.):

```bash
echo 'export ANTHROPIC_API_KEY="your-api-key-here"' >> ~/.bashrc
source ~/.bashrc
```

Get an API key at: https://console.anthropic.com/

## Usage

### Basic Command Format

```bash
node generate.js "<your natural language command>"
```

### Example Commands

**Add regular club events for a month:**
```bash
node generate.js "add rows for December's club events"
```

**Add specific event types:**
```bash
node generate.js "add library events for January 2025"
```

**Add 5th Friday events:**
```bash
node generate.js "add 5th Friday event for January 2025"
```

**Add a custom tournament:**
```bash
node generate.js "add tournament on 12/15/24 called 'Winter Classic' at Jefferson School from 10am-5pm"
```

**Mix and match:**
```bash
node generate.js "add club events and library events for February 2025"
```

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
- `rules.json` - Event templates and venue information
- `generate.js` - Main script

## Workflow

1. Run command to add events
2. Review the output to confirm events
3. Open `events.tsv` in a text editor
4. Copy all contents
5. Paste into your Google Sheet

## Customization

### Adding New Venues

Edit `rules.json` and add to the `venues` section:

```json
"new_venue": {
  "name": "Venue Name",
  "url": "https://google.maps/..."
}
```

### Adding New Event Patterns

Edit `rules.json` and add to the `event_patterns` section:

```json
"new_pattern": {
  "description": "Description for the LLM",
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

## Troubleshooting

**API Key Error**
```
Error: ANTHROPIC_API_KEY environment variable not set
```
Solution: Set the environment variable as shown in Setup section.

**No events added**
- Check your command phrasing
- Make sure the month/dates are valid
- Verify the event type matches defined patterns

**Date parsing issues**
- The tool expects dates in M/D/YY format
- Current year context is 2024

## Examples of What You Can Say

- "add rows for November's club events"
- "add December open gameplay sessions"
- "add all regular events for January 2025"
- "add tournament on 3/15/25 called 'Spring Championship' at Walker Square"
- "add 5th Friday events for all of 2025"
- "add library events for the next 3 months"

The AI will interpret your command and generate the appropriate events!
