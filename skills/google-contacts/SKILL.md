---
name: google-contacts
description: Google Contacts management (search, create, list contacts)
requires-approval:
  create_contact: true
---

# Google Contacts Skill

Manage your Google Contacts using the People API.

## Tools

- `search_contacts` - Search for contacts by name or email (no approval required)
  - Parameters: query, max_results
- `list_contacts` - List all your contacts (no approval required)
  - Parameters: max_results
- `create_contact` - Create a new contact (requires approval)
  - Parameters: name (required), email, phone, company, notes

## Usage Examples

- "Search for John in my contacts"
- "Show me all my contacts"
- "Create a contact for John Smith with email john@email.com and phone 555-1234"
- "Add a contact for Jane Doe from Acme Inc"

## Approval

Create contact operations require user approval before execution.

## Notes

- Contacts are stored in your Google account
- You can search by name or email address
- Phone numbers and company info can be added when creating contacts
