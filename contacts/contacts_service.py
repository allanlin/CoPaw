# -*- coding: utf-8 -*-
"""Google People API service for contacts."""

import os

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from copaw.agents.auth.google_oauth import get_credentials


def _get_people_service():
    """Get authenticated People API service.

    Returns:
        googleapiclient.discovery.Resource or None if not authenticated
    """
    credentials = get_credentials()
    if credentials is None:
        return None

    try:
        service = build("people", "v1", credentials=credentials, cache_discovery=False)
        return service
    except Exception:
        return None