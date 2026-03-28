# -*- coding: utf-8 -*-
"""Image generation tool using MiniMax API."""

import base64
import os

import requests
from agentscope.message import TextBlock
from agentscope.tool import ToolResponse
from PIL import Image


def _validate_image(image_path: str) -> bool:
    """Validate if an image file can be opened and is not corrupted."""
    try:
        with Image.open(image_path) as img:
            img.verify()
        with Image.open(image_path) as img:
            img.load()
        return True
    except Exception as e:
        print(f"Warning: Image '{image_path}' is invalid or corrupted: {e}")
        return False


async def generate_image(
    prompt: str,
    aspect_ratio: str = "16:9",
    reference_images: list[str] | None = None,
) -> ToolResponse:
    """Generate an image from text prompt using MiniMax API.

    Args:
        prompt: Text description of the desired image.
        aspect_ratio: Image dimensions (e.g., "16:9", "9:16", "1:1").
        reference_images: Optional list of reference image paths for image-to-image.
    """
    api_key = os.getenv("MINIMAX_API_KEY")
    if not api_key:
        return ToolResponse(
            content=[TextBlock(type="text", text="MINIMAX_API_KEY is not set. Please configure your MiniMax API key.")],
        )

    # Handle aspect ratio mapping
    aspect_ratio_map = {
        "16:9": "16:9",
        "9:16": "9:16",
        "1:1": "1:1",
        "4:3": "4:3",
        "3:4": "3:4",
        "21:9": "21:9",
    }
    mapped_aspect_ratio = aspect_ratio_map.get(aspect_ratio, "16:9")

    # Build request payload
    payload = {
        "model": "image-01",
        "prompt": prompt,
        "aspect_ratio": mapped_aspect_ratio,
        "response_format": "base64",
    }

    # Add reference images if provided
    if reference_images:
        valid_refs = [img for img in reference_images if _validate_image(img)]
        if valid_refs:
            subject_refs = []
            for ref_img in valid_refs:
                with open(ref_img, "rb") as f:
                    image_b64 = base64.b64encode(f.read()).decode("utf-8")
                subject_refs.append({
                    "type": "character",
                    "image_base64": image_b64
                })
            payload["subject_reference"] = subject_refs

    try:
        response = requests.post(
            "https://api.minimax.io/v1/image_generation",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
        )
        response.raise_for_status()
        json_response = response.json()

        # Extract base64 image
        if "data" in json_response and "image_base64" in json_response["data"]:
            base64_images = json_response["data"]["image_base64"]
            if isinstance(base64_images, list):
                base64_image = base64_images[0]
            else:
                base64_image = base64_images

            # Save to file
            output_dir = os.path.expanduser("~/.copaw/generated")
            os.makedirs(output_dir, exist_ok=True)
            output_file = os.path.join(output_dir, f"image_{base64.b64encode(os.urandom(8)).hex()}.png")

            with open(output_file, "wb") as f:
                f.write(base64.b64decode(base64_image))

            return ToolResponse(
                content=[TextBlock(type="text", text=f"Image generated successfully: {output_file}")],
            )
        else:
            return ToolResponse(
                content=[TextBlock(type="text", text=f"Failed to generate image: {json_response}")],
            )

    except Exception as e:
        return ToolResponse(
            content=[TextBlock(type="text", text=f"Error generating image: {str(e)}")],
        )