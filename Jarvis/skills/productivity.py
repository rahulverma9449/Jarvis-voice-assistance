import json
import re
from datetime import datetime
from urllib.parse import quote_plus

from Jarvis.config import DATA_DIR
from Jarvis.core.history import history


NOTES_FILE = DATA_DIR / "notes.json"


def notes_command(query: str) -> tuple[str, str, str | None]:
    if query.startswith(("read my notes", "show notes", "open notes")):
        if not NOTES_FILE.exists():
            return "You don't have any saved notes yet.", "speak", None
        notes = json.loads(NOTES_FILE.read_text(encoding="utf-8"))
        if not notes:
            return "You don't have any saved notes yet.", "speak", None
        latest = "; ".join(note["text"] for note in notes[-5:])
        return f"Your latest notes are: {latest}", "speak", None
    text = re.sub(r"^(take|create|write|save)\s+(?:a\s+)?note(?:\s+(?:that|to|about))?\s*", "", query).strip()
    if not text:
        return "Say take a note followed by what you want me to remember.", "speak", None
    notes = json.loads(NOTES_FILE.read_text(encoding="utf-8")) if NOTES_FILE.exists() else []
    notes.append({"timestamp": datetime.now().astimezone().isoformat(), "text": text})
    NOTES_FILE.write_text(json.dumps(notes, indent=2, ensure_ascii=False), encoding="utf-8")
    return "I saved your note.", "speak", None


def show_history(query: str) -> tuple[str, str, str | None]:
    match = re.search(r"last\s+(\d+)", query)
    limit = min(int(match.group(1)), 50) if match else 10
    records = history.recent(limit)
    if not records:
        return "Your command history is empty.", "speak", None
    commands = "; ".join(item["command"] for item in records)
    return f"Your last {len(records)} commands were: {commands}", "speak", None


def study_mode(query: str) -> tuple[str, str, str | None]:
    topic = re.sub(r"^start\s+", "", query).replace("study mode", "").replace("interview", "interview preparation").strip()
    topic = topic or "computer science"
    url = f"https://www.google.com/search?q={quote_plus(topic + ' learning roadmap tutorials practice')}"
    return f"Starting {topic} study mode. I opened a focused learning roadmap.", "open_url", url
