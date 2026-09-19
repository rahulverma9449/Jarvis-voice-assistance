"""Thread-safe JSON persistence for product workspace features."""

import json
from pathlib import Path
from threading import RLock
from typing import Any
from uuid import uuid4

from Jarvis.config import DATA_DIR


class WorkspaceStore:
    def __init__(self, path: Path = DATA_DIR / "workspace.json") -> None:
        self.path = path
        self.lock = RLock()

    def _read(self) -> dict[str, list[dict[str, Any]]]:
        if not self.path.exists():
            return {"favorites": [], "reminders": [], "notes": []}
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            return {name: list(data.get(name, [])) for name in ("favorites", "reminders", "notes")}
        except (OSError, json.JSONDecodeError, TypeError):
            return {"favorites": [], "reminders": [], "notes": []}

    def _write(self, data: dict[str, list[dict[str, Any]]]) -> None:
        temporary = self.path.with_suffix(".tmp")
        temporary.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        temporary.replace(self.path)

    def list(self, collection: str) -> list[dict[str, Any]]:
        with self.lock:
            return list(reversed(self._read()[collection]))

    def create(self, collection: str, values: dict[str, Any]) -> dict[str, Any]:
        with self.lock:
            data = self._read()
            record = {"id": uuid4().hex[:12], **values}
            data[collection].append(record)
            self._write(data)
            return record

    def update(self, collection: str, record_id: str, values: dict[str, Any]) -> dict[str, Any] | None:
        with self.lock:
            data = self._read()
            for record in data[collection]:
                if record["id"] == record_id:
                    record.update({key: value for key, value in values.items() if value is not None})
                    self._write(data)
                    return record
            return None

    def delete(self, collection: str, record_id: str) -> bool:
        with self.lock:
            data = self._read()
            original = len(data[collection])
            data[collection] = [item for item in data[collection] if item["id"] != record_id]
            if len(data[collection]) == original:
                return False
            self._write(data)
            return True


workspace = WorkspaceStore()
