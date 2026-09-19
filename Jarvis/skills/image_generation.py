import base64
from datetime import datetime

import requests

from Jarvis.config import GENERATED_IMAGE_DIR, IMAGE_MODEL, OPENAI_API_KEY


def generate_image(query: str) -> tuple[str, str, str | None]:
    prompt = query
    lowered = query.lower()
    for prefix in ("generate an image of", "generate image of", "create an image of", "create image of", "draw"):
        if lowered.startswith(prefix):
            prompt = query[len(prefix):].strip()
            break
    if not prompt:
        return "Tell me what image you would like me to create.", "speak", None
    if not OPENAI_API_KEY:
        return "Image generation is unavailable because the OpenAI key is not configured.", "speak", None
    try:
        response = requests.post(
            "https://api.openai.com/v1/images/generations",
            headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
            json={"model": IMAGE_MODEL, "prompt": prompt, "size": "1024x1024", "quality": "medium"},
            timeout=120,
        )
        response.raise_for_status()
        encoded = response.json()["data"][0]["b64_json"]
        filename = f"jarvis-{datetime.now():%Y%m%d-%H%M%S}.png"
        (GENERATED_IMAGE_DIR / filename).write_bytes(base64.b64decode(encoded))
        return f"I created an image of {prompt}.", "show_image", f"/generated/{filename}"
    except (requests.RequestException, KeyError, IndexError, TypeError, ValueError):
        return "I couldn't generate that image. Check the image API access and try again.", "speak", None
