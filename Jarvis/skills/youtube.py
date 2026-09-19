import re
import webbrowser
from urllib.parse import quote_plus

from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError


def _song_query(query: str) -> str:
    cleaned = query.lower()
    cleaned = re.sub(r"\b(open|launch)\s+youtube\b", " ", cleaned)
    cleaned = re.sub(r"\byoutube\b", " ", cleaned)
    cleaned = re.sub(r"\b(and|then|please)\b", " ", cleaned)
    cleaned = re.sub(r"\b(play|search|find)\b", " ", cleaned)
    cleaned = re.sub(r"\b(the|for|on)\b", " ", cleaned)
    return " ".join(cleaned.split()) or "Punjabi songs"


def youtube_command(query: str) -> tuple[str, str, str | None]:
    term = _song_query(query)
    search_url = f"https://www.youtube.com/results?search_query={quote_plus(term)}"
    try:
        options = {"quiet": True, "no_warnings": True, "extract_flat": True, "playlistend": 1}
        with YoutubeDL(options) as youtube:
            result = youtube.extract_info(f"ytsearch1:{term}", download=False)
        entry = next(iter(result.get("entries") or []))
        video_id = entry.get("id")
        if not video_id:
            raise ValueError("YouTube result has no video id")
        video_url = f"https://www.youtube.com/watch?v={video_id}&autoplay=1"
        webbrowser.open(video_url, new=2)
        title = entry.get("title") or term
        return f"Opening YouTube and playing {title}.", "speak", None
    except (DownloadError, KeyError, TypeError, ValueError, StopIteration):
        webbrowser.open(search_url, new=2)
        return f"I opened YouTube results for {term}. Select a song to play.", "speak", None
