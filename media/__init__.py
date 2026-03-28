# -*- coding: utf-8 -*-
"""MiniMax media generation tools (image, video, music, voice)."""

from copaw.agents.tools.media.image_generator import generate_image
from copaw.agents.tools.media.video_generator import generate_video
from copaw.agents.tools.media.music_generator import generate_music
from copaw.agents.tools.media.voice_generator import text_to_speech, voice_clone, voice_design

__all__ = [
    "generate_image",
    "generate_video",
    "generate_music",
    "text_to_speech",
    "voice_clone",
    "voice_design",
]