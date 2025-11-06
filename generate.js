#!/usr/bin/env node

const Anthropic = require('@anthropic-ai/sdk');
const fs = require('fs');
const path = require('path');
const { parse } = require('csv-parse/sync');
const { stringify } = require('csv-stringify/sync');
const {
  format,
  parse: parseDate,
  addMonths,
  startOfMonth,
  endOfMonth,
  eachDayOfInterval,
  getDay,
  isFriday,
  isWednesday,
  getDate
} = require('date-fns');

// File paths
const EVENTS_FILE = path.join(__dirname, 'events.tsv');
const RULES_FILE = path.join(__dirname, 'rules.json');

// Load rules
function loadRules() {
  const rulesContent = fs.readFileSync(RULES_FILE, 'utf-8');
  return JSON.parse(rulesContent);
}

// Load existing events
function loadEvents() {
  if (!fs.existsSync(EVENTS_FILE)) {
    return [];
  }
  const content = fs.readFileSync(EVENTS_FILE, 'utf-8');
  return parse(content, {
    columns: true,
    delimiter: '\t',
    skip_empty_lines: true
  });
}

// Save events back to TSV
function saveEvents(events) {
  // Sort by date
  events.sort((a, b) => {
    const dateA = parseEventDate(a.Date);
    const dateB = parseEventDate(b.Date);
    return dateA - dateB;
  });

  const output = stringify(events, {
    header: true,
    delimiter: '\t',
    columns: ['Date', 'Name', 'Time', 'Location', 'location_URL', 'Info', 'info_url']
  });

  fs.writeFileSync(EVENTS_FILE, output);
}

// Parse date from M/D/YY format
function parseEventDate(dateStr) {
  const [month, day, year] = dateStr.split('/').map(n => parseInt(n));
  return new Date(2000 + year, month - 1, day);
}

// Format date to M/D/YY format
function formatEventDate(date) {
  const month = date.getMonth() + 1;
  const day = date.getDate();
  const year = date.getFullYear() % 100;
  return `${month}/${day}/${year}`;
}

// Get nth occurrence of a weekday in a month
function getNthWeekdayOfMonth(year, month, weekday, nth) {
  // weekday: 0=Sunday, 5=Friday, 3=Wednesday
  const firstDay = new Date(year, month, 1);
  const lastDay = new Date(year, month + 1, 0);

  const days = eachDayOfInterval({ start: firstDay, end: lastDay })
    .filter(date => getDay(date) === weekday);

  if (nth > days.length) return null;
  return days[nth - 1];
}

// Call Anthropic API to parse command
async function parseCommandWithLLM(command, rules) {
  const apiKey = process.env.ANTHROPIC_API_KEY;
  if (!apiKey) {
    throw new Error('ANTHROPIC_API_KEY environment variable not set. Please set it to use this tool.');
  }

  const client = new Anthropic({ apiKey });

  const systemPrompt = `You are an event generation assistant for a Scrabble club. Your job is to interpret natural language commands and generate structured event data.

Here are the event patterns and templates available:
${JSON.stringify(rules, null, 2)}

Current date context: Today is November 6, 2024.

When given a command, you should:
1. Identify which event pattern(s) are being requested
2. Determine the date(s) for the events
3. Return a JSON array of events to be added

Each event should have this structure:
{
  "Date": "M/D/YY",
  "Name": "event name",
  "Time": "time range",
  "Location": "venue name",
  "location_URL": "google maps url",
  "Info": "additional info",
  "info_url": "optional url"
}

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
{
  "events": [array of event objects],
  "explanation": "brief explanation of what was added"
}`;

  const response = await client.messages.create({
    model: 'claude-3-5-sonnet-20241022',
    max_tokens: 4096,
    messages: [{
      role: 'user',
      content: command
    }],
    system: systemPrompt
  });

  const responseText = response.content[0].text;

  // Try to parse JSON from response
  try {
    return JSON.parse(responseText);
  } catch (e) {
    // Try to extract JSON if it's wrapped in markdown
    const jsonMatch = responseText.match(/```json\n([\s\S]*?)\n```/) ||
                     responseText.match(/```\n([\s\S]*?)\n```/);
    if (jsonMatch) {
      return JSON.parse(jsonMatch[1]);
    }
    throw new Error('Failed to parse LLM response as JSON: ' + responseText);
  }
}

// Main function
async function main() {
  const command = process.argv.slice(2).join(' ');

  if (!command) {
    console.error('Usage: node generate.js "<command>"');
    console.error('Example: node generate.js "add rows for November\'s club events"');
    process.exit(1);
  }

  console.log(`Processing command: "${command}"\n`);

  try {
    // Load data
    const rules = loadRules();
    const existingEvents = loadEvents();

    // Parse command with LLM
    console.log('Interpreting command with AI...');
    const result = await parseCommandWithLLM(command, rules);

    if (!result.events || result.events.length === 0) {
      console.log('No events to add.');
      return;
    }

    console.log(`\n${result.explanation}\n`);
    console.log(`Adding ${result.events.length} event(s):\n`);

    // Display events to be added
    result.events.forEach((event, idx) => {
      console.log(`${idx + 1}. ${event.Date} - ${event.Name} at ${event.Location}`);
    });

    // Add new events
    const allEvents = [...existingEvents, ...result.events];

    // Save back to file
    saveEvents(allEvents);

    console.log(`\n✓ Successfully added ${result.events.length} event(s) to ${EVENTS_FILE}`);
    console.log('You can now copy-paste the contents into your Google Sheet.');

  } catch (error) {
    console.error('Error:', error.message);
    process.exit(1);
  }
}

main();
