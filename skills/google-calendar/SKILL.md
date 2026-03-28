---
name: google-calendar
description: Google Calendar operations (list, create, edit, delete events, search across all calendars)
requires-approval:
  create_event: true
  edit_event: true
  delete_event: true
  quick_add: true
---

# Google Calendar Skill

Manage your Google Calendar with the following capabilities:

## Tools

- `list_events` - List upcoming events from a specific calendar (no approval required)
  - Parameters: time_min, time_max (RFC3339), max_results, calendar_id (defaults to "primary")
- `list_calendars` - List all your Google calendars (no approval required)
- `search_events` - Search for events across all or specific calendars (no approval required)
  - Parameters: query, calendar_id (optional), time_min, time_max, max_results
- `get_event` - Get details of a specific event (no approval required)
  - Parameters: event_id
- `quick_add` - Quick add event using natural language (requires approval)
  - Parameters: text (e.g., "Dinner with John tomorrow at 7pm")
- `create_event` - Create new calendar event (requires approval)
  - Parameters: summary, start_time, end_time, description, location, attendees
- `edit_event` - Modify existing event (requires approval)
  - Parameters: event_id, summary, start_time, end_time, description, location
- `delete_event` - Remove event (requires approval)
  - Parameters: event_id

## Calendar IDs

Common calendar IDs:
- "primary" - Your primary Google calendar
- "allanlin@gmail.com" - Your primary calendar (explicit)
- Other IDs from list_calendars

## Usage Examples

- "What's on my calendar tomorrow?"
- "List all my calendars"
- "Show events on AL & PQ Adventures calendar"
- "Search for 'skiing' across all my calendars"
- "Show me details of my next meeting"
- "Quick add Lunch with Sarah next Friday at noon"
- "Schedule a team meeting next Monday at 2pm"
- "Search for events in April"

## Time Format

All times must be in RFC3339 format, e.g., "2026-03-27T14:00:00-04:00"

## Approval

Create, edit, delete, and quick_add operations require user approval before execution as they modify your calendar.
