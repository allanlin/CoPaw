# -*- coding: utf-8 -*-
"""Voice tools using MiniMax API (text-to-speech, voice clone, voice design)."""

import base64
import os

import requests
from agentscope.message import TextBlock
from agentscope.tool import ToolResponse


async def text_to_speech(
    text: str,
    model: str = "speech-02-hd",
    voice_id: str | None = None,
) -> ToolResponse:
    """Convert text to speech using MiniMax API.

    Args:
        text: Text content to convert to speech.
        model: TTS model to use (default: speech-02-hd).
        voice_id: Optional specific voice ID to use.
    """
    api_key = os.getenv("MINIMAX_API_KEY")
    if not api_key:
        return ToolResponse(
            content=[TextBlock(type="text", text="MINIMAX_API_KEY is not set. Please configure your MiniMax API key.")],
        )

    payload = {
        "model": model,
        "text": text,
    }

    if voice_id:
        payload["voice_id"] = voice_id

    try:
        response = requests.post(
            "https://api.minimax.io/v1/t2a",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
        )
        response.raise_for_status()
        result = response.json()

        if "data" in result and "audio_file" in result["data"]:
            # Save audio file
            output_dir = os.path.expanduser("~/.copaw/generated")
            os.makedirs(output_dir, exist_ok=True)
            output_file = os.path.join(output_dir, f"tts_{base64.b64encode(os.urandom(8)).hex()}.mp3")

            audio_data = result["data"]["audio_file"]
            with open(output_file, "wb") as f:
                f.write(base64.b64decode(audio_data))

            return ToolResponse(
                content=[TextBlock(type="text", text=f"Text-to-speech generated: {output_file}")],
            )

        return ToolResponse(
            content=[TextBlock(type="text", text=f"Text-to-speech generated: {result}")],
        )

    except Exception as e:
        return ToolResponse(
            content=[TextBlock(type="text", text=f"Error generating speech: {str(e)}")],
        )


async def voice_clone(
    audio_file: str,
    text: str | None = None,
) -> ToolResponse:
    """Clone a voice from an audio file using MiniMax API.

    Args:
        audio_file: Path to reference audio file for voice cloning.
        text: Optional text to generate with the cloned voice.
    """
    api_key = os.getenv("MINIMAX_API_KEY")
    if not api_key:
        return ToolResponse(
            content=[TextBlock(type="text", text="MINIMAX_API_KEY is not set. Please configure your MiniMax API key.")],
        )

    try:
        with open(audio_file, "rb") as f:
            audio_b64 = base64.b64encode(f.read()).decode("utf-8")

        payload = {
            "model": "speech-02-hd",
            "voice_file": audio_b64,
        }

        if text:
            payload["text"] = text

        response = requests.post(
            "https://api.minimax.io/v1/voice_clone",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
        )
        response.raise_for_status()
        result = response.json()

        return ToolResponse(
            content=[TextBlock(type="text", text=f"Voice cloned successfully: {result}")],
        )

    except Exception as e:
        return ToolResponse(
            content=[TextBlock(type="text", text=f"Error cloning voice: {str(e)}")],
        )


async def voice_design(
    description: str,
    text: str | None = None,
) -> ToolResponse:
    """Generate a custom voice from text description using MiniMax API.

    Args:
        description: Text description of the desired voice characteristics.
        text: Optional text to generate with the designed voice.
    """
    api_key = os.getenv("MINIMAX_API_KEY")
    if not api_key:
        return ToolResponse(
            content=[TextBlock(type="text", text="MINIMAX_API_KEY is not set. Please configure your MiniMax API key.")],
        )

    payload = {
        "model": "speech-02-hd",
        "description": description,
    }

    if text:
        payload["text"] = text

    try:
        response = requests.post(
            "https://api.minimax.io/v1/voice_design",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
        )
        response.raise_for_status()
        result = response.json()

        return ToolResponse(
            content=[TextBlock(type="text", text=f"Voice designed successfully: {result}")],
        )

    except Exception as e:
        return ToolResponse(
            content=[TextBlock(type="text", text=f"Error designing voice: {str(e)}")],
        )