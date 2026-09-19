import wikipedia


def search_wikipedia(query: str) -> tuple[str, str, str | None]:
    term = query.replace("wikipedia", "").replace("search", "").strip()
    if not term:
        return "What should I search for on Wikipedia?", "speak", None
    try:
        return wikipedia.summary(term, sentences=2, auto_suggest=False), "speak", None
    except wikipedia.exceptions.DisambiguationError as exc:
        return f"Please be more specific. Did you mean {', '.join(exc.options[:3])}?", "speak", None
    except wikipedia.exceptions.PageError:
        return f"I couldn't find a Wikipedia page for {term}.", "speak", None
    except Exception:
        return "Wikipedia is unavailable right now.", "speak", None
