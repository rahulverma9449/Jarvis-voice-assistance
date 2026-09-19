import re

from Jarvis.ai.memory import load_memory, remember


def is_memory_command(query: str) -> bool:
    return query.startswith("remember that ") or query.startswith(("what do you remember about ", "recall "))


def memory_command(query: str) -> tuple[str, str, str | None]:
    if query.startswith("remember that "):
        detail = query.removeprefix("remember that ").strip()
        match = re.match(r"(.+?)\s+is\s+(.+)", detail)
        if not match:
            return "Say remember that, followed by a detail such as my favorite color is blue.", "speak", None
        key, value = match.group(1).strip(), match.group(2).strip()
        remember(key, value)
        return f"I'll remember that {key} is {value}.", "speak", None
    key = re.sub(r"^(what do you remember about|recall)\s+", "", query).strip().rstrip("?")
    memory = load_memory()
    value = memory.get(key)
    if value is None:
        return f"I don't have anything saved about {key}.", "speak", None
    return f"I remember that {key} is {value}.", "speak", None
