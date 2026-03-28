# -*- coding: utf-8 -*-
"""Gmail tools using correct CoPaw async/ToolResponse pattern."""

from agentscope.message import TextBlock
from agentscope.tool import ToolResponse

from copaw.agents.tools.email.gmail_service import _get_gmail_service


async def read_emails(
    query: str | None = None,
    max_results: int = 10,
) -> ToolResponse:
    """Read emails from Gmail inbox.

    Args:
        query: Search query to filter emails (e.g., 'from:example.com is:unread').
               If None, returns recent emails.
        max_results: Maximum number of emails to return (default 10).
    """
    service = _get_gmail_service()
    if service is None:
        return ToolResponse(
            content=[TextBlock(type="text", text="Not authenticated. Please run Google OAuth authentication first.")],
        )

    try:
        search_query = query if query else ""

        results = (
            service.users()
            .messages()
            .list(userId="me", q=search_query, maxResults=max_results)
            .execute()
        )

        messages = results.get("messages", [])

        if not messages:
            return ToolResponse(
                content=[TextBlock(type="text", text="No emails found.")],
            )

        result = ["Emails:"]
        for msg in messages:
            msg_detail = (
                service.users()
                .messages()
                .get(userId="me", id=msg["id"], format="metadata")
                .execute()
            )

            headers = msg_detail["payload"]["headers"]
            subject = next((h["value"] for h in headers if h["name"] == "Subject"), "No Subject")
            sender = next((h["value"] for h in headers if h["name"] == "From"), "Unknown")
            date = next((h["value"] for h in headers if h["name"] == "Date"), "Unknown")

            result.append(f"- From: {sender}")
            result.append(f"  Subject: {subject}")
            result.append(f"  Date: {date}")
            result.append(f"  ID: {msg['id']}")
            result.append("")

        return ToolResponse(
            content=[TextBlock(type="text", text="\n".join(result))],
        )

    except Exception as e:
        return ToolResponse(
            content=[TextBlock(type="text", text=f"Error reading emails: {str(e)}")],
        )


async def create_draft(
    to: str,
    subject: str,
    body: str,
) -> ToolResponse:
    """Create a Gmail draft (does not send).

    Args:
        to: Recipient email address.
        subject: Email subject line.
        body: Email body content.
    """
    service = _get_gmail_service()
    if service is None:
        return ToolResponse(
            content=[TextBlock(type="text", text="Not authenticated. Please run Google OAuth authentication first.")],
        )

    try:
        from base64 import urlsafe_b64encode

        message = (
            f"To: {to}\r\n"
            f"Subject: {subject}\r\n"
            f"\r\n"
            f"{body}"
        )

        encoded_message = urlsafe_b64encode(message.encode("utf-8")).decode("utf-8")

        draft = {
            "message": {
                "raw": encoded_message
            }
        }

        result = (
            service.users()
            .drafts()
            .create(userId="me", body=draft)
            .execute()
        )

        return ToolResponse(
            content=[TextBlock(type="text", text=f"Draft created: {result['id']}")],
        )

    except Exception as e:
        return ToolResponse(
            content=[TextBlock(type="text", text=f"Error creating draft: {str(e)}")],
        )


async def delete_email(message_id: str) -> ToolResponse:
    """Delete an email by moving it to trash.

    Args:
        message_id: The ID of the message to delete.
    """
    service = _get_gmail_service()
    if service is None:
        return ToolResponse(
            content=[TextBlock(type="text", text="Not authenticated. Please run Google OAuth authentication first.")],
        )

    try:
        service.users().messages().trash(userId="me", id=message_id).execute()
        return ToolResponse(
            content=[TextBlock(type="text", text=f"Email {message_id} moved to trash.")],
        )

    except Exception as e:
        return ToolResponse(
            content=[TextBlock(type="text", text=f"Error deleting email: {str(e)}")],
        )


async def move_email(message_id: str, dest_label: str) -> ToolResponse:
    """Move an email to a different label/folder.

    Args:
        message_id: The ID of the message to move.
        dest_label: Destination label (e.g., 'INBOX', '[Gmail]/Starred', 'Work').
    """
    service = _get_gmail_service()
    if service is None:
        return ToolResponse(
            content=[TextBlock(type="text", text="Not authenticated. Please run Google OAuth authentication first.")],
        )

    try:
        message = service.users().messages().get(userId="me", id=message_id).execute()

        current_labels = message.get("labelIds", [])
        new_labels = [dest_label] + [l for l in current_labels if l != "TRASH"]

        service.users().messages().modify(
            userId="me",
            id=message_id,
            body={"removeLabelIds": [], "addLabelIds": new_labels}
        ).execute()

        return ToolResponse(
            content=[TextBlock(type="text", text=f"Email {message_id} moved to {dest_label}.")],
        )

    except Exception as e:
        return ToolResponse(
            content=[TextBlock(type="text", text=f"Error moving email: {str(e)}")],
        )