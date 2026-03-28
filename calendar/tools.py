# -*- coding: utf-8 -*-
"""Google Calendar tools using correct CoPaw async/ToolResponse pattern."""

from datetime import datetime, timedelta

from agentscope.message import TextBlock
from agentscope.tool import ToolResponse

from copaw.agents.tools.calendar.calendar_service import _get_calendar_service


async def list_events(
    time_min: str | None = None,
    time_max: str | None = None,
    max_results: int = 10,
    calendar_id: str = "primary",
) -> ToolResponse:
    """List upcoming Google Calendar events.

    Args:
        time_min: Start time in RFC3339 format (e.g., 2024-01-01T00:00:00Z). Defaults to now.
        time_max: End time in RFC3339 format. Defaults to 7 days from now.
        max_results: Maximum number of events to return (default 10).
        calendar_id: Calendar ID to query. Use "primary" for your main calendar,
            or a specific calendar ID (e.g., from list_calendars).
            Defaults to "primary".
    """
    service = _get_calendar_service()
    if service is None:
        return ToolResponse(
            content=[TextBlock(type="text", text="Not authenticated. Please run Google OAuth authentication first.")],
        )

    if time_min is None:
        time_min = datetime.utcnow().isoformat() + "Z"
    if time_max is None:
        time_max = (datetime.utcnow() + timedelta(days=7)).isoformat() + "Z"

    try:
        events_result = (
            service.events()
            .list(
                calendarId=calendar_id,
                timeMin=time_min,
                timeMax=time_max,
                maxResults=max_results,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )

        events = events_result.get("items", [])

        if not events:
            return ToolResponse(
                content=[TextBlock(type="text", text="No upcoming events found.")],
            )

        result = ["Upcoming events:"]
        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            summary = event.get("summary", "No title")
            event_id = event["id"]
            result.append(f"- {start}: {summary} (ID: {event_id})")

        return ToolResponse(
            content=[TextBlock(type="text", text="\n".join(result))],
        )

    except Exception as e:
        return ToolResponse(
            content=[TextBlock(type="text", text=f"Error listing events: {str(e)}")],
        )


async def create_event(
    summary: str,
    start_time: str,
    end_time: str,
    description: str | None = None,
    location: str | None = None,
    attendees: str | None = None,
) -> ToolResponse:
    """Create a Google Calendar event.

    Args:
        summary: Title/summary of the event (required).
        start_time: Start time in RFC3339 format (e.g., 2024-01-01T10:00:00Z).
        end_time: End time in RFC3339 format (e.g., 2024-01-01T11:00:00Z).
        description: Optional description for the event.
        location: Optional location for the event.
        attendees: Optional comma-separated list of email addresses.
    """
    service = _get_calendar_service()
    if service is None:
        return ToolResponse(
            content=[TextBlock(type="text", text="Not authenticated. Please run Google OAuth authentication first.")],
        )

    event = {
        "summary": summary,
        "start": {"dateTime": start_time},
        "end": {"dateTime": end_time},
    }

    if description:
        event["description"] = description
    if location:
        event["location"] = location
    if attendees:
        attendee_list = [{"email": email.strip()} for email in attendees.split(",")]
        event["attendees"] = attendee_list

    try:
        event_result = service.events().insert(calendarId="primary", body=event).execute()
        return ToolResponse(
            content=[TextBlock(type="text", text=f"Event created: {event_result.get('htmlLink')}")],
        )

    except Exception as e:
        return ToolResponse(
            content=[TextBlock(type="text", text=f"Error creating event: {str(e)}")],
        )


async def edit_event(
    event_id: str,
    summary: str | None = None,
    start_time: str | None = None,
    end_time: str | None = None,
    description: str | None = None,
    location: str | None = None,
) -> ToolResponse:
    """Modify an existing Google Calendar event.

    Uses Google Calendar API PATCH endpoint for partial updates.
    Only provided fields are updated.

    Args:
        event_id: The ID of the event to modify (required).
        summary: New title/summary of the event.
        start_time: New start time in RFC3339 format.
        end_time: New end time in RFC3339 format.
        description: New description for the event.
        location: New location for the event.
    """
    service = _get_calendar_service()
    if service is None:
        return ToolResponse(
            content=[TextBlock(type="text", text="Not authenticated. Please run Google OAuth authentication first.")],
        )

    # Build event dict with only provided fields
    event = {}
    if summary is not None:
        event["summary"] = summary
    if start_time is not None:
        event["start"] = {"dateTime": start_time}
    if end_time is not None:
        event["end"] = {"dateTime": end_time}
    if description is not None:
        event["description"] = description
    if location is not None:
        event["location"] = location

    if not event:
        return ToolResponse(
            content=[TextBlock(type="text", text="No fields to update. Please provide at least one field.")],
        )

    try:
        event_result = service.events().patch(
            calendarId="primary",
            eventId=event_id,
            body=event
        ).execute()
        return ToolResponse(
            content=[TextBlock(type="text", text=f"Event updated: {event_result.get('htmlLink')}")],
        )

    except Exception as e:
        return ToolResponse(
            content=[TextBlock(type="text", text=f"Error editing event: {str(e)}")],
        )


async def delete_event(event_id: str) -> ToolResponse:
    """Delete a Google Calendar event.

    Args:
        event_id: The ID of the event to delete.
    """
    service = _get_calendar_service()
    if service is None:
        return ToolResponse(
            content=[TextBlock(type="text", text="Not authenticated. Please run Google OAuth authentication first.")],
        )

    try:
        service.events().delete(calendarId="primary", eventId=event_id).execute()
        return ToolResponse(
            content=[TextBlock(type="text", text=f"Event {event_id} deleted successfully.")],
        )

    except Exception as e:
        return ToolResponse(
            content=[TextBlock(type="text", text=f"Error deleting event: {str(e)}")],
        )


async def list_calendars() -> ToolResponse:
    """List all calendars available in the user's Google account.

    Returns a list of all calendars with their IDs and display names.
    """
    service = _get_calendar_service()
    if service is None:
        return ToolResponse(
            content=[TextBlock(type="text", text="Not authenticated. Please run Google OAuth authentication first.")],
        )

    try:
        calendar_list = service.calendarList().list().execute()
        calendars = calendar_list.get("items", [])

        if not calendars:
            return ToolResponse(
                content=[TextBlock(type="text", text="No calendars found.")],
            )

        result = ["Your calendars:"]
        for cal in calendars:
            summary = cal.get("summary", "No name")
            cal_id = cal.get("id", "")
            primary = " (primary)" if cal.get("primary") else ""
            result.append(f"- {summary}{primary} (ID: {cal_id})")

        return ToolResponse(
            content=[TextBlock(type="text", text="\n".join(result))],
        )

    except Exception as e:
        return ToolResponse(
            content=[TextBlock(type="text", text=f"Error listing calendars: {str(e)}")],
        )


async def quick_add(text: str) -> ToolResponse:
    """Quick add an event using natural language.

    Args:
        text: Natural language text for the event (e.g., "Dinner with John tomorrow at 7pm").
    """
    service = _get_calendar_service()
    if service is None:
        return ToolResponse(
            content=[TextBlock(type="text", text="Not authenticated. Please run Google OAuth authentication first.")],
        )

    try:
        event_result = service.events().quickAdd(
            calendarId="primary",
            text=text,
        ).execute()

        return ToolResponse(
            content=[TextBlock(type="text", text=f"Event created: {event_result.get('summary')} ({event_result.get('htmlLink')})")],
        )

    except Exception as e:
        return ToolResponse(
            content=[TextBlock(type="text", text=f"Error creating event: {str(e)}")],
        )


async def get_event(event_id: str, calendar_id: str = "primary") -> ToolResponse:
    """Get details of a specific calendar event.

    Args:
        event_id: The ID of the event to retrieve.
        calendar_id: The calendar ID the event belongs to. Defaults to "primary".
    """
    service = _get_calendar_service()
    if service is None:
        return ToolResponse(
            content=[TextBlock(type="text", text="Not authenticated. Please run Google OAuth authentication first.")],
        )

    try:
        event = service.events().get(
            calendarId=calendar_id,
            eventId=event_id,
        ).execute()

        summary = event.get("summary", "No title")
        start = event.get("start", {}).get("dateTime", event.get("start", {}).get("date", "TBD"))
        end = event.get("end", {}).get("dateTime", event.get("end", {}).get("date", "TBD"))
        description = event.get("description", "No description")
        location = event.get("location", "No location")
        event_id = event.get("id", "")

        result = [
            f"Event: {summary}",
            f"ID: {event_id}",
            f"Start: {start}",
            f"End: {end}",
            f"Location: {location}",
            f"Description: {description}",
        ]

        return ToolResponse(
            content=[TextBlock(type="text", text="\n".join(result))],
        )

    except Exception as e:
        return ToolResponse(
            content=[TextBlock(type="text", text=f"Error getting event: {str(e)}")],
        )


async def search_events(
    query: str,
    calendar_id: str | None = None,
    time_min: str | None = None,
    time_max: str | None = None,
    max_results: int = 20,
) -> ToolResponse:
    """Search for events across calendars.

    Args:
        query: Free-text search query to match events.
        calendar_id: Optional specific calendar ID to search. If None, searches all calendars.
        time_min: Start time in RFC3339 format. Defaults to now.
        time_max: End time in RFC3339 format. Defaults to 30 days from now.
        max_results: Maximum number of events to return (default 20).
    """
    service = _get_calendar_service()
    if service is None:
        return ToolResponse(
            content=[TextBlock(type="text", text="Not authenticated. Please run Google OAuth authentication first.")],
        )

    if time_min is None:
        time_min = datetime.utcnow().isoformat() + "Z"
    if time_max is None:
        time_max = (datetime.utcnow() + timedelta(days=30)).isoformat() + "Z"

    try:
        # Build list of calendar IDs to search
        if calendar_id:
            calendar_ids = [calendar_id]
        else:
            # Get all calendar IDs
            calendar_list = service.calendarList().list().execute()
            calendar_ids = [c["id"] for c in calendar_list.get("items", [])]

        all_events = []
        for cal_id in calendar_ids:
            try:
                events_result = service.events().list(
                    calendarId=cal_id,
                    q=query,
                    timeMin=time_min,
                    timeMax=time_max,
                    maxResults=max_results,
                    singleEvents=True,
                    orderBy="startTime",
                ).execute()
                for event in events_result.get("items", []):
                    event["_calendar_id"] = cal_id
                    all_events.append(event)
            except Exception:
                # Skip calendars we don't have access to
                continue

        if not all_events:
            return ToolResponse(
                content=[TextBlock(type="text", text=f"No events found matching '{query}'.")],
            )

        # Sort by start time
        all_events.sort(key=lambda e: e.get("start", {}).get("dateTime", e.get("start", {}).get("date", "")))

        result = [f"Found {len(all_events)} event(s) matching '{query}':"]
        for event in all_events[:max_results]:
            start = event["start"].get("dateTime", event["start"].get("date", "TBD"))
            summary = event.get("summary", "No title")
            cal_id = event.get("_calendar_id", "unknown")
            result.append(f"- {start}: {summary} (Calendar: {cal_id})")

        return ToolResponse(
            content=[TextBlock(type="text", text="\n".join(result))],
        )

    except Exception as e:
        return ToolResponse(
            content=[TextBlock(type="text", text=f"Error searching events: {str(e)}")],
        )
