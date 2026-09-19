import requests

from Jarvis.config import (
    ANTHROPIC_API_KEY,
    ANTHROPIC_MODEL,
    GROQ_API_KEY,
    GROQ_MODEL,
    OPENAI_API_KEY,
    OPENAI_MODEL,
)


SYSTEM_PROMPT = (
    "You are Jarvis, Rahul's concise and helpful desktop assistant. "
    "Give a direct, accurate answer suitable for speaking aloud. "
    "Do not claim to have performed actions you cannot perform."
)


def _groq(query: str) -> str:
    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
        json={
            "model": GROQ_MODEL,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": query},
            ],
            "temperature": 0.4,
            "max_tokens": 400,
        },
        timeout=25,
    )
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"].strip()


def _openai(query: str) -> str:
    response = requests.post(
        "https://api.openai.com/v1/responses",
        headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
        json={
            "model": OPENAI_MODEL,
            "instructions": SYSTEM_PROMPT,
            "input": query,
            "max_output_tokens": 400,
            "store": False,
        },
        timeout=30,
    )
    response.raise_for_status()
    for item in response.json().get("output", []):
        for content in item.get("content", []):
            if content.get("type") == "output_text" and content.get("text"):
                return content["text"].strip()
    raise ValueError("OpenAI returned no text output")


def _anthropic(query: str) -> str:
    response = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01",
        },
        json={
            "model": ANTHROPIC_MODEL,
            "system": SYSTEM_PROMPT,
            "messages": [{"role": "user", "content": query}],
            "max_tokens": 400,
        },
        timeout=30,
    )
    response.raise_for_status()
    blocks = response.json().get("content", [])
    text = " ".join(block["text"] for block in blocks if block.get("type") == "text")
    if not text:
        raise ValueError("Anthropic returned no text output")
    return text.strip()


def provider_status() -> dict[str, bool]:
    return {
        "groq": bool(GROQ_API_KEY),
        "openai": bool(OPENAI_API_KEY),
        "anthropic": bool(ANTHROPIC_API_KEY),
    }


def ask_ai(query: str) -> str:
    providers = (
        (GROQ_API_KEY, _groq),
        (OPENAI_API_KEY, _openai),
        (ANTHROPIC_API_KEY, _anthropic),
    )
    configured = False
    for api_key, provider in providers:
        if not api_key:
            continue
        configured = True
        try:
            return provider(query)
        except (requests.RequestException, KeyError, IndexError, TypeError, ValueError):
            continue
    if configured:
        return "All configured AI providers are temporarily unavailable. Please try again shortly."
    return "No AI provider is configured. Add a provider key to the .env file and restart Jarvis."
