import os
import re
import subprocess
import sys
from datetime import datetime

from Jarvis.config import PROJECT_DIR


def is_developer_command(query: str) -> bool:
    return query.startswith((
        "create python file", "run python", "run jarvis.py", "open requirements.txt",
        "install python package",
    ))


def developer_command(query: str) -> tuple[str, str, str | None]:
    if query.startswith("create python file"):
        requested = query.removeprefix("create python file").strip()
        safe_name = re.sub(r"[^a-zA-Z0-9_-]", "_", requested).strip("_")
        filename = f"{safe_name or 'python_file_' + datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
        path = PROJECT_DIR / filename
        path.touch(exist_ok=False)
        os.startfile(path)
        return f"Created and opened {filename}.", "speak", None

    if query == "open requirements.txt":
        path = PROJECT_DIR / "requirements.txt"
        os.startfile(path)
        return "Opening requirements.txt.", "speak", None

    if query.startswith("install python package"):
        package = query.removeprefix("install python package").strip()
        if not re.fullmatch(r"[a-zA-Z0-9_.-]+", package):
            return "Say install Python package followed by one valid package name.", "speak", None
        subprocess.Popen([sys.executable, "-m", "pip", "install", package], cwd=PROJECT_DIR)
        return f"Installing the Python package {package}.", "speak", None

    script = PROJECT_DIR / "Jarvis" / "jarvis.py" if "jarvis.py" in query else None
    if script:
        subprocess.Popen([sys.executable, str(script)], cwd=PROJECT_DIR)
        return "Running jarvis.py.", "speak", None

    subprocess.Popen([sys.executable], cwd=PROJECT_DIR)
    return "Starting Python.", "speak", None
