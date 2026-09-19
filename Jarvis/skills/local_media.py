import os
from pathlib import Path


AUDIO_EXTENSIONS = {".mp3", ".wav", ".m4a", ".aac", ".flac", ".ogg"}
VIDEO_EXTENSIONS = {".mp4", ".mkv", ".avi", ".mov", ".wmv", ".webm"}


def is_local_media_command(query: str) -> bool:
    return any(phrase in query for phrase in (
        "play mp3", "play mp4", "play local", "play video from computer", "play music from computer",
        "play downloaded movie", "play songs from my music folder", "open my videos", "play movie",
    ))


def _find(folder: Path, extensions: set[str], term: str) -> Path | None:
    if not folder.exists():
        return None
    candidates = (path for path in folder.rglob("*") if path.is_file() and path.suffix.lower() in extensions)
    if term:
        candidates = (path for path in candidates if term in path.stem.lower())
    return next(candidates, None)


def play_local_media(query: str) -> tuple[str, str, str | None]:
    video = any(word in query for word in ("mp4", "video", "movie"))
    folder = Path.home() / ("Videos" if video else "Music")
    extensions = VIDEO_EXTENSIONS if video else AUDIO_EXTENSIONS
    term = query
    for phrase in ("play downloaded movie", "play video from computer", "play music from computer", "play songs from my music folder", "open my videos", "play local video", "play local music", "play local songs", "play movie", "play mp4", "play mp3"):
        term = term.replace(phrase, "")
    term = term.strip().lower()
    match = _find(folder, extensions, term)
    if not match:
        return f"I couldn't find matching {'video' if video else 'audio'} in your {folder.name} folder.", "speak", None
    os.startfile(match)
    return f"Playing {match.stem}.", "speak", None
