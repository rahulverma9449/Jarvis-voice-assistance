from Jarvis.config import ASSISTANT_NAME


WAKE_WORDS = (ASSISTANT_NAME.lower(), "hi jarvis", "hey jarvis", "okay jarvis")


def strip_wake_word(command: str) -> tuple[str, bool]:
    cleaned = command.strip().lower()
    for wake_word in WAKE_WORDS:
        if cleaned.startswith(wake_word):
            return cleaned.removeprefix(wake_word).strip(" ,"), True
    return cleaned, False
