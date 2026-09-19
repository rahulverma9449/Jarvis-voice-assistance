"""Twenty product-grade REST endpoints for the Jarvis workspace."""

from collections import Counter
from datetime import datetime
import json
import secrets
import string
from typing import Literal

from fastapi import APIRouter, HTTPException, Query, Response
from pydantic import BaseModel, Field, field_validator

from Jarvis.config import ASSISTANT_NAME
from Jarvis.core.capabilities import CAPABILITIES, capability_dicts
from Jarvis.core.history import history
from Jarvis.core.workspace_store import workspace
from Jarvis.skills.utilities import utility_command


router = APIRouter(prefix="/api/v2", tags=["Jarvis Pro Workspace"])


class FavoriteCreate(BaseModel):
    capability_id: str = Field(min_length=1, max_length=100)


class ReminderCreate(BaseModel):
    title: str = Field(min_length=1, max_length=160)
    due_at: datetime


class ReminderUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=160)
    due_at: datetime | None = None
    completed: bool | None = None


class NoteCreate(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    content: str = Field(min_length=1, max_length=5000)


class ExpressionRequest(BaseModel):
    expression: str = Field(min_length=1, max_length=200)


class ConversionRequest(BaseModel):
    value: float = Field(ge=-1e12, le=1e12)
    source_unit: str = Field(min_length=1, max_length=30)
    target_unit: str = Field(min_length=1, max_length=30)


class TextRequest(BaseModel):
    text: str = Field(min_length=1, max_length=10000)
    operation: Literal["uppercase", "lowercase", "titlecase", "reverse", "word_count", "trim"]


def _records() -> list[dict]:
    return history.recent(10_000)


# 1
@router.get("/analytics/summary")
def analytics_summary() -> dict:
    records = _records()
    actions = Counter(item.get("action", "unknown") for item in records)
    return {"total_commands": len(records), "unique_commands": len({item.get("command", "").casefold() for item in records}), "actions": actions, "capabilities": len(CAPABILITIES)}


# 2
@router.get("/analytics/timeline")
def analytics_timeline(days: int = Query(7, ge=1, le=90)) -> list[dict]:
    counts: Counter[str] = Counter()
    for item in _records():
        try:
            day = datetime.fromisoformat(item["timestamp"]).date().isoformat()
            counts[day] += 1
        except (KeyError, TypeError, ValueError):
            continue
    return [{"date": day, "commands": count} for day, count in sorted(counts.items())[-days:]]


# 3
@router.get("/analytics/actions")
def analytics_actions() -> list[dict]:
    counts = Counter(item.get("action", "unknown") for item in _records())
    return [{"action": action, "count": count} for action, count in counts.most_common()]


# 4
@router.get("/commands/search")
def command_search(q: str = Query(min_length=1, max_length=100), limit: int = Query(12, ge=1, le=50)) -> dict:
    items = capability_dicts(search=q)[:limit]
    return {"query": q, "total": len(items), "items": items}


# 5
@router.get("/commands/suggestions")
def command_suggestions(limit: int = Query(6, ge=1, le=20)) -> list[dict]:
    used = Counter(item.get("command", "").casefold() for item in _records())
    ranked = sorted(CAPABILITIES, key=lambda item: (-used[item.example.casefold()], item.title))
    return [item.to_dict() for item in ranked[:limit]]


# 6
@router.get("/favorites")
def list_favorites() -> list[dict]:
    return workspace.list("favorites")


# 7
@router.post("/favorites", status_code=201)
def create_favorite(payload: FavoriteCreate) -> dict:
    match = next((item for item in CAPABILITIES if item.id == payload.capability_id), None)
    if not match:
        raise HTTPException(404, "Capability not found")
    existing = next((item for item in workspace.list("favorites") if item["capability_id"] == match.id), None)
    return existing or workspace.create("favorites", {"capability_id": match.id, "title": match.title, "example": match.example, "created_at": datetime.now().astimezone().isoformat()})


# 8
@router.delete("/favorites/{favorite_id}", status_code=204)
def delete_favorite(favorite_id: str) -> Response:
    if not workspace.delete("favorites", favorite_id):
        raise HTTPException(404, "Favorite not found")
    return Response(status_code=204)


# 9
@router.get("/reminders")
def list_reminders(include_completed: bool = False) -> list[dict]:
    items = workspace.list("reminders")
    return items if include_completed else [item for item in items if not item.get("completed")]


# 10
@router.post("/reminders", status_code=201)
def create_reminder(payload: ReminderCreate) -> dict:
    return workspace.create("reminders", {"title": payload.title.strip(), "due_at": payload.due_at.isoformat(), "completed": False, "created_at": datetime.now().astimezone().isoformat()})


# 11
@router.patch("/reminders/{reminder_id}")
def update_reminder(reminder_id: str, payload: ReminderUpdate) -> dict:
    values = payload.model_dump(exclude_unset=True)
    if isinstance(values.get("due_at"), datetime):
        values["due_at"] = values["due_at"].isoformat()
    record = workspace.update("reminders", reminder_id, values)
    if not record:
        raise HTTPException(404, "Reminder not found")
    return record


# 12
@router.delete("/reminders/{reminder_id}", status_code=204)
def delete_reminder(reminder_id: str) -> Response:
    if not workspace.delete("reminders", reminder_id):
        raise HTTPException(404, "Reminder not found")
    return Response(status_code=204)


# 13
@router.get("/notes")
def list_notes(search: str | None = Query(default=None, max_length=100)) -> list[dict]:
    items = workspace.list("notes")
    if search:
        needle = search.casefold()
        items = [item for item in items if needle in f"{item['title']} {item['content']}".casefold()]
    return items


# 14
@router.post("/notes", status_code=201)
def create_note(payload: NoteCreate) -> dict:
    return workspace.create("notes", {"title": payload.title.strip(), "content": payload.content.strip(), "created_at": datetime.now().astimezone().isoformat()})


# 15
@router.delete("/notes/{note_id}", status_code=204)
def delete_note(note_id: str) -> Response:
    if not workspace.delete("notes", note_id):
        raise HTTPException(404, "Note not found")
    return Response(status_code=204)


# 16
@router.post("/tools/calculate")
def calculate(payload: ExpressionRequest) -> dict:
    reply, _, _ = utility_command(f"calculate {payload.expression.casefold()}")
    if reply.startswith("I couldn't"):
        raise HTTPException(422, reply)
    return {"expression": payload.expression, "result": reply.removeprefix("The answer is ").removesuffix(".").replace(",", ""), "spoken": reply}


# 17
@router.post("/tools/convert")
def convert(payload: ConversionRequest) -> dict:
    command = f"convert {payload.value:g} {payload.source_unit.casefold()} to {payload.target_unit.casefold()}"
    reply, _, _ = utility_command(command)
    if "don't have a conversion" in reply or reply.startswith("Say convert"):
        raise HTTPException(422, reply)
    return {"input": payload.model_dump(), "spoken": reply}


# 18
@router.post("/tools/text")
def transform_text(payload: TextRequest) -> dict:
    operations = {"uppercase": str.upper, "lowercase": str.lower, "titlecase": str.title, "reverse": lambda value: value[::-1], "trim": lambda value: " ".join(value.split())}
    if payload.operation == "word_count":
        return {"operation": payload.operation, "result": {"words": len(payload.text.split()), "characters": len(payload.text)}}
    return {"operation": payload.operation, "result": operations[payload.operation](payload.text)}


# 19
@router.get("/tools/password")
def generate_password(length: int = Query(20, ge=12, le=128)) -> dict:
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    while True:
        password = "".join(secrets.choice(alphabet) for _ in range(length))
        if all(any(char in group for char in password) for group in (string.ascii_lowercase, string.ascii_uppercase, string.digits, "!@#$%^&*")):
            return {"password": password, "length": length, "generated_by": ASSISTANT_NAME}


# 20
@router.get("/export/history")
def export_history() -> Response:
    content = json.dumps({"exported_at": datetime.now().astimezone().isoformat(), "records": _records()}, indent=2, ensure_ascii=False)
    return Response(content=content, media_type="application/json", headers={"Content-Disposition": "attachment; filename=jarvis-history.json"})
