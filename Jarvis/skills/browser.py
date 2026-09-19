from urllib.parse import quote_plus


def browser_command(query: str) -> tuple[str, str, str | None]:
    if "open google" in query:
        return "Opening Google.", "open_url", "https://google.com"
    term = query.removeprefix("search google for ").strip()
    return f"Searching Google for {term}.", "open_url", f"https://www.google.com/search?q={quote_plus(term)}"
