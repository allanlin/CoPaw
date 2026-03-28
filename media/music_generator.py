# -*- coding: utf-8 -*-
"""Music generation tool using MiniMax API."""

import os

import requests
from agentscope.message import TextBlock
from agentscope.tool import ToolResponse


async def generate_music(
    prompt: str,
    lyrics: str | None = None,
    is_instrumental: bool = False,
) -> ToolResponse:
    """Generate music from text prompt using MiniMax API.

    Args:
        prompt: Style, mood, and scenario description (e.g., "Soulful Blues, Rainy Night, Melancholy").
        lyrics: Optional song lyrics with structure markers (Verse, Chorus, Bridge, etc.).
        is_instrumental: Set true for instrumental-only output.
    """
    api_key = os.getenv("MINIMAX_API_KEY")
    if not api_key:
        return ToolResponse(
            content=[TextBlock(type="text", text="MINIMAX_API_KEY is not set. Please configure your MiniMax API key.")],
        )

    payload = {
        "model": "music-2.5+",
        "prompt": prompt,
        "is_instrumental": is_instrumental,
    }

    if lyrics:
        payload["lyrics"] = lyrics

    try:
        response = requests.post(
            "https://api.minimax.io/v1/music_generation",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
        )
        response.raise_for_status()
        result = response.json()

        # MiniMax returns a task_id for async processing
        if "task_id" in result:
            return ToolResponse(
                content=[TextBlock(type="text", text=f"Music generation started (task_id: {result['task_id']}). Polling for completion...")],
            )
        elif "data" in result and "audio_url" in result["data"]:
            return ToolResponse(
                content=[TextBlock(type="text", text=f"Music generated: {result['data']['audio_url']}")],
            )
        else:
            return ToolResponse(
                content=[TextBlock(type="text", text=f"Music generated: {result}")],
            )

    except Exception as e:
        return ToolResponse(
            content=[TextBlock(type="text", text=f"Error generating music: {str(e)}")],
        )