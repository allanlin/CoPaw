# -*- coding: utf-8 -*-
# flake8: noqa: E501
# pylint: disable=line-too-long,too-many-return-statements
import base64
import os
import mimetypes
import unicodedata

from agentscope.tool import ToolResponse
from agentscope.message import (
    TextBlock,
    ImageBlock,
    AudioBlock,
    VideoBlock,
)

from ..schema import FileBlock


def _auto_as_type(mt: str) -> str:
    if mt.startswith("image/"):
        return "image"
    if mt.startswith("audio/"):
        return "audio"
    if mt.startswith("video/"):
        return "video"
    return "file"


async def send_file_to_user(
    file_path: str,
) -> ToolResponse:
    """Send a file to the user.

    Args:
        file_path (`str`):
            Path to the file to send.

    Returns:
        `ToolResponse`:
            The tool response containing the file or an error message.
    """

    # Normalize the path: expand ~ and fix Unicode normalization differences
    # (e.g. macOS stores filenames as NFD but paths from the LLM arrive as NFC,
    # causing os.path.exists to return False for files that do exist).
    file_path = os.path.expanduser(unicodedata.normalize("NFC", file_path))

    if not os.path.exists(file_path):
        return ToolResponse(
            content=[
                TextBlock(
                    type="text",
                    text=f"Error: The file {file_path} does not exist.",
                ),
            ],
        )

    if not os.path.isfile(file_path):
        return ToolResponse(
            content=[
                TextBlock(
                    type="text",
                    text=f"Error: The path {file_path} is not a file.",
                ),
            ],
        )

    # Detect MIME type
    mime_type, _ = mimetypes.guess_type(file_path)
    if mime_type is None:
        # Default to application/octet-stream for unknown types
        mime_type = "application/octet-stream"
    as_type = _auto_as_type(mime_type)

    try:
        # Read file and create data URL for reliable browser access
        with open(file_path, "rb") as f:
            file_data = base64.b64encode(f.read()).decode("utf-8")

        if as_type == "image":
            # Return as FileBlock with data URL for download
            data_url = f"data:{mime_type};base64,{file_data}"
            return ToolResponse(
                content=[
                    FileBlock(
                        type="file",
                        source={"type": "url", "url": data_url},
                        filename=os.path.basename(file_path),
                    ),
                    TextBlock(type="text", text=f"Image: {os.path.basename(file_path)} ({os.path.getsize(file_path) // 1024}KB) - Click to download"),
                ],
            )
        if as_type == "audio":
            data_url = f"data:{mime_type};base64,{file_data}"
            return ToolResponse(
                content=[
                    AudioBlock(type="audio", source={"type": "url", "url": data_url}),
                    TextBlock(type="text", text="File sent successfully."),
                ],
            )
        if as_type == "video":
            data_url = f"data:{mime_type};base64,{file_data}"
            return ToolResponse(
                content=[
                    VideoBlock(type="video", source={"type": "url", "url": data_url}),
                    TextBlock(type="text", text="File sent successfully."),
                ],
            )

        # For generic files, create data URL and include download info
        data_url = f"data:{mime_type};base64,{file_data}"
        return ToolResponse(
            content=[
                FileBlock(
                    type="file",
                    source={"type": "url", "url": data_url},
                    filename=os.path.basename(file_path),
                ),
                TextBlock(type="text", text=f"File sent: {os.path.basename(file_path)}"),
            ],
        )

    except Exception as e:
        return ToolResponse(
            content=[
                TextBlock(
                    type="text",
                    text=f"Error: Send file failed due to \n{e}",
                ),
            ],
        )
