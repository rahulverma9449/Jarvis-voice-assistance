import json
from datetime import datetime
from pathlib import Path

from Jarvis.config import BROWSER_DATA_FILE


class BrowserDataStore:
    """Local append-only cache for Jira and Confluence command results."""

    def __init__(self, path: Path = BROWSER_DATA_FILE) -> None:
        self.path = path

    def add(self, source: str, command: str, reply: str, url: str | None = None) -> None:
        record = {
            "timestamp": datetime.now().astimezone().isoformat(),
            "source": source,
            "command": command,
            "reply": reply,
            "url": url,
        }
        with self.path.open("a", encoding="utf-8") as file:
            file.write(json.dumps(record, ensure_ascii=False) + "\n")

    def recent(self, limit: int = 30) -> list[dict]:
        if not self.path.exists():
            return []
        lines = self.path.read_text(encoding="utf-8").splitlines()[-limit:]
        return [json.loads(line) for line in lines if line.strip()]


browser_data = BrowserDataStore()
