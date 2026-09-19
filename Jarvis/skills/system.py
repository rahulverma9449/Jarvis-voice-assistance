import platform
import shutil
import os

import pyautogui


def system_status(_: str) -> tuple[str, str, str | None]:
    return f"Jarvis is running on {platform.system()} {platform.release()}.", "speak", None


def protected_power_action(query: str) -> tuple[str, str, str | None]:
    action = "restart" if "restart" in query else "shutdown"
    return f"For safety, {action} commands are disabled in the web interface.", "speak", None


def media_control(query: str) -> tuple[str, str, str | None]:
    controls = {
        "volume up": ("volumeup", "Increasing volume."), "volume down": ("volumedown", "Decreasing volume."),
        "mute": ("volumemute", "Toggling mute."), "unmute": ("volumemute", "Toggling mute."),
        "pause music": ("playpause", "Pausing music."), "resume music": ("playpause", "Resuming music."),
        "stop music": ("stop", "Stopping music."), "next song": ("nexttrack", "Playing the next track."),
        "previous song": ("prevtrack", "Playing the previous track."),
    }
    phrase = next((name for name in controls if name in query), None)
    if not phrase:
        return "I couldn't identify that media control.", "speak", None
    key, reply = controls[phrase]
    pyautogui.press(key)
    return reply, "speak", None


def computer_health(_: str) -> tuple[str, str, str | None]:
    disk = shutil.disk_usage("C:\\")
    free_gb = disk.free / (1024 ** 3)
    total_gb = disk.total / (1024 ** 3)
    return f"This computer has {free_gb:.0f} gigabytes free out of {total_gb:.0f}, and {os.cpu_count()} logical CPU cores.", "speak", None
