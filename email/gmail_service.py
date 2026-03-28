# -*- coding: utf-8 -*-
"""Gmail API service wrapper."""

from googleapiclient.discovery import build

from copaw.agents.auth.google_oauth import get_credentials


def _get_gmail_service():
    """Get authenticated Gmail service.

    Returns:
        Gmail API service or None if not authenticated.
    """
    credentials = get_credentials()
    if credentials is None:
        return None
    return build("gmail", "v1", credentials=credentials, cache_discovery=False)