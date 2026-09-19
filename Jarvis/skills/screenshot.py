from datetime import datetime

import pyautogui

from Jarvis.config import SCREENSHOT_DIR


def take_screenshot(_: str) -> tuple[str, str, str | None]:
    path = SCREENSHOT_DIR / f"screenshot-{datetime.now():%Y%m%d-%H%M%S}.png"
    pyautogui.screenshot().save(path)
    return f"Screenshot saved as {path.name}.", "speak", None
