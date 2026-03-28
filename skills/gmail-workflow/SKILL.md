---
name: gmail-workflow
description: Manage Gmail inbox, drafts, and organization
requires-approval:
  delete_email: true
  move_email: false
---

# Gmail Workflow Skill

Manage your Gmail inbox with the following capabilities:

## Tools

- `read_emails` - Search inbox with Gmail query syntax (no approval required)
- `create_draft` - Create email draft for you to send manually (no approval required)
- `delete_email` - Trash an email (requires approval)
- `move_email` - Move email to label/folder (no approval required)

## Usage Examples

- "Show my unread emails from today"
- "Create a draft email to john@example.com about the meeting"
- "Move the email from amazon to shopping label"
- "Delete that spam email"

## Approval

Delete operations require user approval before execution as they are destructive.
