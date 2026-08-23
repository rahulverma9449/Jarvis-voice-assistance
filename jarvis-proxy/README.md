# J.A.R.V.I.S. Voice Assistant — Complete Project

A browser-based voice assistant (`jarvis-voice-assistant.html`) backed by a
small local FastAPI proxy (`server.py`) that talks to Claude (and optionally
Groq as a fallback). Includes built-in commands (time, timers, reminders,
opening sites, search, math, jokes) plus free-form Q&A, wake-by-clap,
wake-by-whistle, and hands-free Conversation Mode.

## Files

| File                          | Purpose                                              |
|--------------------------------|-------------------------------------------------------|
| `jarvis-voice-assistant.html` | The entire UI — open this in a browser (or via server) |
| `server.py`                   | Local proxy that holds your real API key server-side  |
| `requirements.txt`            | Python dependencies for the proxy                      |
| `.env.example`                | Template for your API key — copy to `.env`             |

## 1. Install dependencies

```bash
pip install -r requirements.txt
```

## 2. Set your API key — this fixes the 401 error you've been seeing

The `401 invalid x-api-key` error means the proxy has no valid Anthropic key
to authenticate with. Fix it like this:

1. Go to **https://console.anthropic.com** → sign in → **Settings → API Keys**.
2. Click **Create Key**, copy it (starts with `sk-ant-...`).
3. Make sure that workspace has billing set up / available credits — a key
   with no credit still returns an auth-style error on some setups.
4. Copy `.env.example` to `.env` in the same folder as `server.py`, and paste
   your real key in:
   ```bash
   cp .env.example .env
   ```
   Then edit `.env`:
   ```
   ANTHROPIC_API_KEY=sk-ant-your-real-key-here
   ```
5. **Do not** use a claude.ai session/browser cookie — it must be a real API
   key generated from the Console above.

(Optional) If you also want a Groq fallback for when Anthropic auth fails,
add a `GROQ_API_KEY` from **https://console.groq.com** to the same `.env`.

## 3. Run the proxy server

```bash
uvicorn server:app --reload --port 8787
```

Check it's healthy and that your key is actually loaded:

```bash
curl http://localhost:8787/health
# {"status":"ok","anthropic_key_configured":true,"groq_key_configured":false}
```

If `anthropic_key_configured` is `false`, the `.env` file isn't being read —
double check it's named exactly `.env` (not `.env.txt`) and sits next to
`server.py`.

## 4. Open Jarvis

Go to **http://localhost:8787/** in your browser (Chrome or Edge recommended
for full Web Speech API support).

**Important:** open it via that `localhost` URL, not by double-clicking the
HTML file directly. Opening it as a raw `file://` page is why the microphone
permission popup kept reappearing — browsers can't persist mic permission for
`file://` origins, only for real http(s)/localhost origins. Via
`http://localhost:8787/`, click **"Allow while visiting the site"** once and
it will stick.

## 5. Using it

- **Type or speak** commands directly — try "what time is it", "open Gmail",
  "set a timer for 2 minutes", "tell me a joke".
- **Conversation Mode** is on by default: Jarvis listens → answers by voice →
  automatically listens again, hands-free.
- **Clap twice** or **whistle** at any time to wake Jarvis without touching
  anything. The 👂 badge on the orb lights up once ambient listening is
  active; a pink flash + toast confirms a wake event was detected.
- Anything not covered by a built-in command (open X, timers, math, etc.) is
  sent to `server.py`, which asks Claude and reads the answer back to you.

## Troubleshooting

| Symptom | Fix |
|---|---|
| `401 invalid x-api-key` | Your `.env` key is missing/wrong — see step 2 above. |
| "I can't reach my reasoning engine. Make sure the local Jarvis proxy server is running on port 8787." | `server.py` isn't running — go back to step 3. |
| Mic permission asks every single time | You opened the raw HTML file (`file://...`) instead of `http://localhost:8787/`. See step 4. |
| "Mic Not Supported" | Your browser doesn't support the Web Speech API — use Chrome or Edge. |
| Clap/whistle wake doesn't trigger | It's heuristic (amplitude + frequency shape), not ML-based. Try clapping closer to the mic, or in a quieter room. Thresholds live in the `detectClap`/`detectWhistle` functions in the HTML's `<script>` if you want to tune them. |
