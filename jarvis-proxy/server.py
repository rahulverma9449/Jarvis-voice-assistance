"""
Jarvis AI proxy — a tiny FastAPI server that sits between the Jarvis voice
assistant (running standalone in your browser) and the Anthropic API.

Why this exists:
Browsers can't safely call api.anthropic.com directly with a real API key —
the key would be exposed in your frontend JS for anyone to read. This proxy
keeps the key on the server side (in an environment variable) and exposes a
single simple endpoint the Jarvis HTML file can call instead.

Run it:
    pip install fastapi uvicorn anthropic
    export ANTHROPIC_API_KEY="sk-ant-..."      # PowerShell: $env:ANTHROPIC_API_KEY="sk-ant-..."
    uvicorn server:app --reload --port 8787

Then open jarvis-voice-assistant.html in your browser as usual — it will
call http://localhost:8787/api/ask instead of Anthropic directly. The
proxy can also fall back to Groq if `GROQ_API_KEY` is configured and
Anthropic authentication fails.
"""

import json
import os
import pathlib
import urllib.error
import urllib.request

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import uvicorn

from dotenv import load_dotenv

try:
    import anthropic
except ImportError:
    anthropic = None

dotenv_path = pathlib.Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=dotenv_path)

ANTHROPIC_API_KEY = (
    os.environ.get("ANTHROPIC_API_KEY")
    or os.environ.get("ANTHROPIC_KEY")
    or os.environ.get("ANTHROPIC_APIKEY")
)
GROQ_API_KEY = (
    os.environ.get("GROQ_API_KEY")
    or os.environ.get("GROQ_API-KEY")
    or os.environ.get("GROQ_KEY")
    or os.environ.get("GROQAPIKEY")
    or os.environ.get("GROQAPI_KEY")
)

app = FastAPI(title="Jarvis AI Proxy")

# Allow the standalone HTML file (opened via file://, origin "null") and any
# localhost dev server to call this API. Since this only runs on your own
# machine for your own use, a permissive CORS policy is fine here.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY) if anthropic and ANTHROPIC_API_KEY else None


class AskRequest(BaseModel):
    question: str


class AskResponse(BaseModel):
    answer: str


SYSTEM_PROMPT = (
    "You are Jarvis, a concise voice assistant. The user is speaking to you "
    "out loud and your reply will be read aloud by text-to-speech. Answer "
    "directly in 1-4 short sentences, plain spoken language, no markdown, "
    "no lists, no headers, no asterisks."
)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "anthropic_key_configured": bool(ANTHROPIC_API_KEY),
        "groq_key_configured": bool(GROQ_API_KEY),
    }


@app.get("/", response_class=FileResponse)
def homepage():
    return FileResponse(
        pathlib.Path(__file__).resolve().parent / "jarvis-voice-assistant.html",
        media_type="text/html",
        headers={
            "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
            "Pragma": "no-cache",
            "Expires": "0",
        },
    )


@app.post("/api/ask", response_model=AskResponse)
def ask(payload: AskRequest):
    question = payload.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="question must not be empty.")

    if not client and not GROQ_API_KEY:
        fallback = (
            "I can hear you, but my AI connection is not configured yet. "
            "Add an Anthropic or Groq API key in the .env file to enable full spoken answers."
        )
        return AskResponse(answer=fallback)
    if not question:
        raise HTTPException(status_code=400, detail="question must not be empty.")

    if client:
        try:
            message = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=1000,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": question}],
            )
            text_blocks = [block.text for block in message.content if block.type == "text"]
            answer = " ".join(text_blocks).strip() or "I processed that, but didn't get a clear answer back."
            return AskResponse(answer=answer)
        except anthropic.APIError as exc:
            if "authentication_error" in str(exc).lower() and GROQ_API_KEY:
                try:
                    return AskResponse(answer=ask_groq(question))
                except Exception as groq_exc:
                    raise HTTPException(status_code=502, detail=f"Anthropic API error: {exc}; Groq fallback failed: {groq_exc}")
            raise HTTPException(status_code=502, detail=f"Anthropic API error: {exc}. Set a valid ANTHROPIC_API_KEY or GROQ_API_KEY to use fallback.")
            
    if GROQ_API_KEY:
        try:
            return AskResponse(answer=ask_groq(question))
        except Exception as exc:
            raise HTTPException(status_code=502, detail=f"Groq API error: {exc}")

    raise HTTPException(
        status_code=500,
        detail=(
            "No valid Anthropic or Groq API key is configured. "
            "Set ANTHROPIC_API_KEY or GROQ_API_KEY in the environment before starting the proxy."
        ),
    )


def ask_groq(question: str) -> str:
    if not GROQ_API_KEY:
        raise RuntimeError("GROQ_API_KEY is not configured.")

    # Groq exposes an OpenAI-compatible chat completions endpoint.
    # See https://console.groq.com/docs/quickstart
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": question},
        ],
        "max_tokens": 1000,
    }
    request = urllib.request.Request(
        "https://api.groq.com/openai/v1/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {GROQ_API_KEY}",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            data = json.load(response)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode(errors="ignore")
        raise RuntimeError(f"Groq API HTTP {exc.code}: {body}")
    except Exception as exc:
        raise RuntimeError(f"Groq API request failed: {exc}")

    try:
        return data["choices"][0]["message"]["content"].strip()
    except (KeyError, IndexError, TypeError):
        return str(data).strip()


if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8787, reload=True)
