# -*- coding: utf-8 -*-
"""Google Calendar API service wrapper."""

from googleapiclient.discovery import build

from copaw.agents.auth.google_oauth import get_credentials


def _get_calendar_service():
    """Get authenticated Google Calendar service.

    Returns:
        Calendar API service or None if not authenticated.
    """
    credentials = get_credentials()
    if credentials is None:
        return None
    return build("calendar", "v3", credentials=credentials, cache_discovery=False)
