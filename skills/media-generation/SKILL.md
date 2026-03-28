---
name: media-generation
description: Generate images, music, and videos using MiniMax AI
requires-approval:
  generate_video: true
  music_generation: true
  voice_clone: true
---

# Media Generation Skill

Generate images, music, and videos using MiniMax AI.

## Tools

- `generate_image` - Text-to-image generation (configurable approval)
  - Parameters: prompt, model, aspect_ratio, resolution
- `generate_music` - Song generation (requires approval - can be costly)
  - Parameters: prompt, duration, instrumental
- `generate_video` - Video generation (requires approval - async, polling required)
  - Parameters: prompt, duration, resolution, fps
- `text_to_speech` - Convert text to audio (no approval required)
  - Parameters: text, voice, speed
- `voice_clone` - Clone voice from audio file (requires approval)
  - Parameters: audio_file, text
- `voice_design` - Create custom voice from text (no approval required)
  - Parameters: text, style

## Usage Examples

- "Generate an image of a sunset over mountains"
- "Create a 30-second ambient music track"
- "Make a video of a robot walking"
- "Read this article aloud in a calm voice"

## Approval

Video generation, music generation, and voice cloning require approval as they may be time-consuming or costly.

## Async Operations

Video generation is asynchronous. After initiating, you may need to poll for the result.
