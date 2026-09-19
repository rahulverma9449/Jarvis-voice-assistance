from urllib.parse import quote_plus


def play_music(query: str) -> tuple[str, str, str | None]:
    term = query.replace("play music", "").replace("play song", "").strip()
    if not term:
        term = "music"
    return f"Finding {term} on YouTube Music.", "open_url", f"https://music.youtube.com/search?q={quote_plus(term)}"
