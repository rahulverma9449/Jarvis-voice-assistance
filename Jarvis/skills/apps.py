import os
import shutil
import subprocess
from pathlib import Path

from Jarvis.config import PROJECT_DIR


ALLOWED_APPS = {
    "notepad": "notepad.exe", "calculator": "calc.exe", "paint": "mspaint.exe",
    "file explorer": "explorer.exe", "command prompt": "cmd.exe", "powershell": "powershell.exe",
    "task manager": "taskmgr.exe", "control panel": "control.exe", "settings": "ms-settings:",
    "vs code": "code", "visual studio code": "code", "chrome": "chrome.exe", "microsoft edge": "msedge.exe",
    "word": "winword.exe", "excel": "excel.exe", "powerpoint": "powerpnt.exe",
    "steam": "steam.exe", "epic games": "EpicGamesLauncher.exe", "xbox": "XboxPcApp.exe",
    "pycharm": "pycharm64.exe", "jupyter notebook": "jupyter-notebook.exe",
    "minecraft": "MinecraftLauncher.exe", "gta": "GTA5.exe", "valorant": "VALORANT.exe",
    "counter strike": "cs2.exe", "fifa": "FIFA23.exe", "cricket game": "cricket.exe",
}
FOLDERS = {
    "downloads": Path.home() / "Downloads", "documents": Path.home() / "Documents",
    "pictures": Path.home() / "Pictures", "music": Path.home() / "Music", "videos": Path.home() / "Videos",
    "my videos": Path.home() / "Videos", "my music folder": Path.home() / "Music",
    "desktop": Path.home() / "Desktop", "jarvis folder": PROJECT_DIR, "jarvis project": PROJECT_DIR,
    "my jarvis project": PROJECT_DIR, "python project": PROJECT_DIR, "my python project": PROJECT_DIR,
    "frontend folder": PROJECT_DIR / "frontend", "backend folder": PROJECT_DIR,
    "screenshot folder": PROJECT_DIR / "Jarvis" / "data" / "screenshots",
}


def is_app_or_folder(query: str) -> bool:
    name = query.removeprefix("open ").strip()
    return name in ALLOWED_APPS or name in FOLDERS


def open_app(query: str) -> tuple[str, str, str | None]:
    name = query.removeprefix("open ").strip()
    if name in FOLDERS:
        path = FOLDERS[name]
        if path.exists():
            os.startfile(path)
            return f"Opening {name}.", "speak", None
        return f"The {name} path does not exist.", "speak", None
    executable = ALLOWED_APPS.get(name)
    if not executable:
        return f"I don't have a safe launcher configured for {name}.", "speak", None
    if executable.startswith("ms-"):
        os.startfile(executable)
    elif shutil.which(executable):
        subprocess.Popen([executable], creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    else:
        return f"I couldn't find {name} on this computer.", "speak", None
    return f"Opening {name}.", "speak", None
