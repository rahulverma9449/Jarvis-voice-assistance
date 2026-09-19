# Jarvis Pro API v2

Jarvis v2.1 adds 20 validated workspace operations under `/api/v2`. Interactive schemas and request testing are available at [`/docs`](http://127.0.0.1:8000/docs).

| # | Method | Endpoint | Purpose |
|---:|:---:|---|---|
| 1 | GET | `/analytics/summary` | Usage and capability totals |
| 2 | GET | `/analytics/timeline` | Daily command activity |
| 3 | GET | `/analytics/actions` | Action-type distribution |
| 4 | GET | `/commands/search` | Search the command catalogue |
| 5 | GET | `/commands/suggestions` | Get smart command suggestions |
| 6 | GET | `/favorites` | List favorite capabilities |
| 7 | POST | `/favorites` | Save a capability |
| 8 | DELETE | `/favorites/{id}` | Remove a favorite |
| 9 | GET | `/reminders` | List active reminders |
| 10 | POST | `/reminders` | Create a reminder |
| 11 | PATCH | `/reminders/{id}` | Edit or complete a reminder |
| 12 | DELETE | `/reminders/{id}` | Delete a reminder |
| 13 | GET | `/notes` | List and search notes |
| 14 | POST | `/notes` | Create a note |
| 15 | DELETE | `/notes/{id}` | Delete a note |
| 16 | POST | `/tools/calculate` | Safely evaluate arithmetic |
| 17 | POST | `/tools/convert` | Convert supported units |
| 18 | POST | `/tools/text` | Apply deterministic text operations |
| 19 | GET | `/tools/password` | Generate a cryptographic password |
| 20 | GET | `/export/history` | Download command history as JSON |

Workspace data is stored locally in `Jarvis/data/workspace.json`. Writes are thread-safe and use atomic file replacement. Input sizes, numeric ranges, enum values, and resource identifiers are validated by FastAPI/Pydantic.

