import json
from datetime import datetime
from pathlib import Path

from Jarvis.config import HISTORY_FILE


class HistoryStore:
    def __init__(self, path: Path = HISTORY_FILE) -> None:
        self.path = path

    def add(self, command: str, reply: str, action: str = "speak") -> None:
        record = {
            "timestamp": datetime.now().astimezone().isoformat(),
            "command": command,
            "reply": reply,
            "action": action,
        }
        with self.path.open("a", encoding="utf-8") as file:
            file.write(json.dumps(record, ensure_ascii=False) + "\n")

    def recent(self, limit: int = 20) -> list[dict]:
        if not self.path.exists():
            return []
        lines = self.path.read_text(encoding="utf-8").splitlines()[-limit:]
        return [json.loads(line) for line in lines if line.strip()]

    def clear(self) -> None:
        self.path.write_text("", encoding="utf-8")


history = HistoryStore()
