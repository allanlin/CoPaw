# -*- coding: utf-8 -*-
"""Video generation tool using MiniMax API (async with polling)."""

import base64
import os
import time

import requests
import warnings
from agentscope.message import TextBlock
from agentscope.tool import ToolResponse

from urllib3.exceptions import InsecureRequestWarning

# Suppress SSL warnings on macOS with LibreSSL
warnings.filterwarnings("ignore", category=InsecureRequestWarning)


async def _poll_for_video_completion(task_id: str, api_key: str, output_file: str, max_wait_seconds: int = 300) -> str:
    """Poll the MiniMax API until video generation is complete."""
    start_time = time.time()
    query_url = "https://api.minimax.io/v1/query/video_generation"

    while time.time() - start_time < max_wait_seconds:
        response = requests.get(
            query_url,
            headers={"Authorization": f"Bearer {api_key}"},
            params={"task_id": task_id},
            verify=False,
        )
        response.raise_for_status()
        result = response.json()

        task_status = result.get("status", "")

        if task_status == "Success":
            file_id = result.get("file_id")
            if file_id:
                # Download video
                files_url = "https://api.minimax.io/v1/files/retrieve"
                files_response = requests.get(
                    files_url,
                    headers={"Authorization": f"Bearer {api_key}"},
                    params={"file_id": file_id},
                    verify=False,
                )
                files_response.raise_for_status()
                file_result = files_response.json()
                download_url = file_result.get("file", {}).get("download_url")

                if download_url:
                    video_response = requests.get(download_url, verify=False)
                    video_response.raise_for_status()
                    with open(output_file, "wb") as f:
                        f.write(video_response.content)
                    return f"Video generated successfully: {output_file}"

        elif task_status == "Fail":
            return f"Video generation failed: {result.get('status_msg', 'Unknown error')}"

        elif task_status in ("Processing", "Queueing", "Preparing"):
            time.sleep(5)
            continue
        else:
            time.sleep(5)
            continue

    return f"Video generation timed out after {max_wait_seconds} seconds"


async def generate_video(
    prompt: str,
    reference_images: list[str] | None = None,
    aspect_ratio: str = "16:9",
) -> ToolResponse:
    """Generate a video from text prompt using MiniMax API.

    This is an async operation that polls for completion.

    Args:
        prompt: Text description of the desired video.
        reference_images: Optional list of reference image paths for image-to-video.
        aspect_ratio: Video dimensions (e.g., "16:9", "9:16", "1:1").
    """
    api_key = os.getenv("MINIMAX_API_KEY")
    if not api_key:
        return ToolResponse(
            content=[TextBlock(type="text", text="MINIMAX_API_KEY is not set. Please configure your MiniMax API key.")],
        )

    # Build request payload
    payload = {
        "model": "T2V-01-Director",
        "prompt": prompt,
    }

    # Add reference images if provided
    if reference_images:
        subject_refs = []
        for ref_img in reference_images:
            try:
                with open(ref_img, "rb") as f:
                    image_b64 = base64.b64encode(f.read()).decode("utf-8")
                subject_refs.append({
                    "type": "character",
                    "image_base64": image_b64
                })
            except Exception as e:
                print(f"Skipping invalid reference image {ref_img}: {e}")
                continue

        if subject_refs:
            payload["subject_reference"] = subject_refs

    try:
        # Start video generation
        response = requests.post(
            "https://api.minimax.io/v1/video_generation",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
            verify=False,
        )
        response.raise_for_status()
        result = response.json()

        task_id = result.get("task_id")
        if not task_id:
            return ToolResponse(
                content=[TextBlock(type="text", text=f"Failed to start video generation: {result}")],
            )

        # Prepare output file
        output_dir = os.path.expanduser("~/.copaw/generated")
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, f"video_{base64.b64encode(os.urandom(8)).hex()}.mp4")

        # Poll for completion
        status = await _poll_for_video_completion(task_id, api_key, output_file)
        return ToolResponse(
            content=[TextBlock(type="text", text=status)],
        )

    except Exception as e:
        return ToolResponse(
            content=[TextBlock(type="text", text=f"Error generating video: {str(e)}")],
        )