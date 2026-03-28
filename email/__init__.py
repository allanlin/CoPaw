# -*- coding: utf-8 -*-
"""Gmail tools for email management."""

from copaw.agents.tools.email.tools import (
    read_emails,
    create_draft,
    delete_email,
    move_email,
)

__all__ = [
    "read_emails",
    "create_draft",
    "delete_email",
    "move_email",
]