import json
from typing import Any

from Jarvis.config import MEMORY_FILE


def load_memory() -> dict[str, Any]:
    if not MEMORY_FILE.exists():
        return {}
    try:
        return json.loads(MEMORY_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def remember(key: str, value: Any) -> None:
    memory = load_memory()
    memory[key] = value
    MEMORY_FILE.write_text(json.dumps(memory, indent=2, ensure_ascii=False), encoding="utf-8")


def forget(key: str) -> bool:
    memory = load_memory()
    existed = key in memory
    memory.pop(key, None)
    MEMORY_FILE.write_text(json.dumps(memory, indent=2, ensure_ascii=False), encoding="utf-8")
    return existed
