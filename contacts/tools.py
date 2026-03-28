# -*- coding: utf-8 -*-
"""Google Contacts tools using People API."""

from agentscope.message import TextBlock
from agentscope.tool import ToolResponse

from copaw.agents.tools.contacts.contacts_service import _get_people_service


async def create_contact(
    name: str,
    email: str | None = None,
    phone: str | None = None,
    company: str | None = None,
    notes: str | None = None,
) -> ToolResponse:
    """Create a new Google contact.

    Args:
        name: Full name of the contact (required).
        email: Email address.
        phone: Phone number.
        company: Company/organization.
        notes: Additional notes.
    """
    service = _get_people_service()
    if service is None:
        return ToolResponse(
            content=[TextBlock(type="text", text="Not authenticated for Google Contacts. Please re-authenticate with contacts scope.")],
        )

    # Build contact body
    contact_body = {
        "names": [{"givenName": name}],
    }

    if email:
        contact_body["emailAddresses"] = [{"value": email}]

    if phone:
        contact_body["phoneNumbers"] = [{"value": phone}]

    if company:
        contact_body["organizations"] = [{"name": company}]

    if notes:
        contact_body["biographies"] = [{"value": notes}]

    try:
        result = service.people().createContact(body=contact_body).execute()
        resource_name = result.get("resourceName", "")
        return ToolResponse(
            content=[TextBlock(type="text", text=f"Contact created: {name} ({resource_name})")],
        )
    except Exception as e:
        return ToolResponse(
            content=[TextBlock(type="text", text=f"Error creating contact: {str(e)}")],
        )


async def search_contacts(query: str, max_results: int = 10) -> ToolResponse:
    """Search for contacts by name or email.

    Args:
        query: Search query (name or email).
        max_results: Maximum number of results to return.
    """
    service = _get_people_service()
    if service is None:
        return ToolResponse(
            content=[TextBlock(type="text", text="Not authenticated for Google Contacts. Please re-authenticate with contacts scope.")],
        )

    try:
        results = service.people().searchContacts(
            query=query,
            readMask="names,emailAddresses,phoneNumbers",
            pageSize=max_results,
        ).execute()

        connections = results.get("results", [])

        if not connections:
            return ToolResponse(
                content=[TextBlock(type="text", text=f"No contacts found matching '{query}'.")],
            )

        result = [f"Found {len(connections)} contact(s):"]
        for item in connections:
            person = item.get("person", {})
            names = person.get("names", [{}])
            name = names[0].get("displayName", "Unknown") if names else "Unknown"
            emails = person.get("emailAddresses", [])
            email = emails[0].get("value", "") if emails else ""
            phones = person.get("phoneNumbers", [])
            phone = phones[0].get("value", "") if phones else ""
            resource = person.get("resourceName", "")

            result.append(f"- {name}")
            if email:
                result.append(f"  Email: {email}")
            if phone:
                result.append(f"  Phone: {phone}")
            result.append(f"  ID: {resource}")

        return ToolResponse(
            content=[TextBlock(type="text", text="\n".join(result))],
        )

    except Exception as e:
        return ToolResponse(
            content=[TextBlock(type="text", text=f"Error searching contacts: {str(e)}")],
        )


async def list_contacts(max_results: int = 20) -> ToolResponse:
    """List all contacts in your Google account.

    Args:
        max_results: Maximum number of contacts to return.
    """
    service = _get_people_service()
    if service is None:
        return ToolResponse(
            content=[TextBlock(type="text", text="Not authenticated for Google Contacts. Please re-authenticate with contacts scope.")],
        )

    try:
        results = service.people().connections().list(
            resourceName="people/me",
            pageSize=max_results,
            personFields="names,emailAddresses,phoneNumbers",
        ).execute()

        connections = results.get("connections", [])

        if not connections:
            return ToolResponse(
                content=[TextBlock(type="text", text="No contacts found.")],
            )

        result = [f"Your contacts ({len(connections)}):"]
        for person in connections:
            names = person.get("names", [{}])
            name = names[0].get("displayName", "Unknown") if names else "Unknown"
            emails = person.get("emailAddresses", [])
            email = emails[0].get("value", "") if emails else ""
            phones = person.get("phoneNumbers", [])
            phone = phones[0].get("value", "") if phones else ""

            result.append(f"- {name}")
            if email:
                result.append(f"  Email: {email}")
            if phone:
                result.append(f"  Phone: {phone}")

        return ToolResponse(
            content=[TextBlock(type="text", text="\n".join(result))],
        )

    except Exception as e:
        return ToolResponse(
            content=[TextBlock(type="text", text=f"Error listing contacts: {str(e)}")],
        )