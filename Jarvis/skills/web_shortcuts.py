import re
from urllib.parse import quote_plus


WEBSITES = {
    "google": "https://google.com", "gmail": "https://mail.google.com", "github": "https://github.com",
    "linkedin": "https://linkedin.com", "chatgpt": "https://chatgpt.com", "stack overflow": "https://stackoverflow.com",
    "w3schools": "https://w3schools.com", "geeksforgeeks": "https://geeksforgeeks.org", "leetcode": "https://leetcode.com",
    "hackerrank": "https://hackerrank.com", "kaggle": "https://kaggle.com", "coursera": "https://coursera.org",
    "udemy": "https://udemy.com", "google classroom": "https://classroom.google.com", "google colab": "https://colab.research.google.com",
    "hugging face": "https://huggingface.co", "pypi": "https://pypi.org", "python documentation": "https://docs.python.org/3/",
    "python docs": "https://docs.python.org/3/", "python official website": "https://python.org", "react docs": "https://react.dev",
    "fastapi docs": "https://fastapi.tiangolo.com", "numpy docs": "https://numpy.org/doc", "pandas docs": "https://pandas.pydata.org/docs",
    "pytorch": "https://pytorch.org", "tensorflow": "https://tensorflow.org", "scikit-learn": "https://scikit-learn.org",
    "docker docs": "https://docs.docker.com", "kubernetes docs": "https://kubernetes.io/docs", "aws docs": "https://docs.aws.amazon.com",
    "openai documentation": "https://platform.openai.com/docs", "kaggle datasets": "https://kaggle.com/datasets",
    "wikipedia": "https://wikipedia.org", "reddit": "https://reddit.com", "instagram": "https://instagram.com", "facebook": "https://facebook.com",
    "whatsapp": "https://web.whatsapp.com", "amazon": "https://amazon.in", "flipkart": "https://flipkart.com",
    "netflix": "https://netflix.com", "prime video": "https://primevideo.com", "hotstar": "https://hotstar.com",
    "google news": "https://news.google.com", "news": "https://news.google.com", "chess": "https://chess.com",
    "online chess": "https://chess.com/play/online", "sudoku": "https://sudoku.com", "solitaire": "https://solitaired.com",
    "snake game": "https://playsnake.org", "racing games": "https://poki.com/en/racing", "cricket games": "https://poki.com/en/cricket",
    "online games": "https://poki.com",
    "localhost": "http://127.0.0.1:5173", "localhost 5173": "http://127.0.0.1:5173", "localhost 8000": "http://127.0.0.1:8000/docs",
}


def is_website_command(query: str) -> bool:
    if not query.startswith("open "):
        return False
    target = query.removeprefix("open ").strip()
    return target in WEBSITES or bool(re.fullmatch(r"(?:https?://)?[\w.-]+\.[a-z]{2,}(?:/\S*)?", target))


def open_website(query: str) -> tuple[str, str, str | None]:
    target = query.removeprefix("open ").strip()
    url = WEBSITES.get(target)
    if not url:
        url = target if target.startswith(("http://", "https://")) else f"https://{target}"
    return f"Opening {target}.", "open_url", url


def search_web(query: str) -> tuple[str, str, str | None]:
    term = re.sub(r"^(google|search(?:\s+for)?|open)\s+", "", query, flags=re.IGNORECASE).strip()
    if not term:
        return "Tell me what you want to search for.", "speak", None
    return f"Searching Google for {term}.", "open_url", f"https://www.google.com/search?q={quote_plus(term)}"
