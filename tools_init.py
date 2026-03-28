# -*- coding: utf-8 -*-
from agentscope.tool import (
    execute_python_code,
    view_text_file,
    write_text_file,
)

from .file_io import (
    read_file,
    write_file,
    edit_file,
    append_file,
)
from .file_search import (
    grep_search,
    glob_search,
)
from .shell import execute_shell_command
from .send_file import send_file_to_user
from .browser_control import browser_use
from .desktop_screenshot import desktop_screenshot
from .view_image import view_image
from .memory_search import create_memory_search_tool
from .get_current_time import get_current_time, set_user_timezone
from .get_token_usage import get_token_usage

# Email tools (Gmail)
from .email import (
    read_emails,
    create_draft,
    delete_email,
    move_email,
)

# Calendar tools (Google Calendar)
from .calendar import (
    list_events,
    create_event,
    edit_event,
    delete_event,
)

# Media tools (MiniMax)
from .media import (
    generate_image,
    generate_video,
    generate_music,
    text_to_speech,
    voice_clone,
    voice_design,
)

__all__ = [
    "execute_python_code",
    "execute_shell_command",
    "view_text_file",
    "write_text_file",
    "read_file",
    "write_file",
    "edit_file",
    "append_file",
    "grep_search",
    "glob_search",
    "send_file_to_user",
    "desktop_screenshot",
    "view_image",
    "browser_use",
    "create_memory_search_tool",
    "get_current_time",
    "set_user_timezone",
    "get_token_usage",
    # Email tools
    "read_emails",
    "create_draft",
    "delete_email",
    "move_email",
    # Calendar tools
    "list_events",
    "create_event",
    "edit_event",
    "delete_event",
    # Media tools
    "generate_image",
    "generate_video",
    "generate_music",
    "text_to_speech",
    "voice_clone",
    "voice_design",
]
