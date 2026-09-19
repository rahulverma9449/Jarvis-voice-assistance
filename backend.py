from pathlib import Path
from datetime import datetime
import os
import platform
import shutil
import time

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from Jarvis.ai.llm import provider_status
from Jarvis.config import GENERATED_IMAGE_DIR
from Jarvis.core.command_router import route_command
from Jarvis.core.browser_datastore import browser_data
from Jarvis.core.history import history
from Jarvis.core.capabilities import CAPABILITIES, capability_dicts, categories
from Jarvis.ai.memory import forget, load_memory, remember
from Jarvis.config import ASSISTANT_NAME, LANGUAGE, PROJECT_DIR, USER_NAME
from Jarvis.core.market_api import router as market_router


STARTED_AT = time.time()


app = FastAPI(
    title="Jarvis Intelligence API",
    description="Voice-first local assistant API with 100+ discoverable capabilities.",
    version="2.1.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(market_router)


class CommandRequest(BaseModel):
    command: str


class CommandResponse(BaseModel):
    reply: str
    action: str = "speak"
    url: str | None = None


class BatchCommandRequest(BaseModel):
    commands: list[str] = Field(min_length=1, max_length=10)


class MemoryRequest(BaseModel):
    key: str = Field(min_length=1, max_length=100)
    value: str = Field(min_length=1, max_length=1000)


@app.get("/api/health")
def health() -> dict:
    return {
        "status": "online", "assistant": ASSISTANT_NAME, "version": "2.1.0",
        "capabilities": len(CAPABILITIES), "uptime_seconds": round(time.time() - STARTED_AT),
        "pro_endpoints": 20,
        "ai_providers": provider_status(),
    }


@app.get("/api/profile")
def profile() -> dict:
    return {"assistant": ASSISTANT_NAME, "user": USER_NAME, "language": LANGUAGE}


@app.get("/api/capabilities")
def capabilities(category: str | None = None, search: str | None = None) -> dict:
    items = capability_dicts(category, search)
    return {"total": len(items), "items": items}


@app.get("/api/capabilities/categories")
def capability_categories() -> list[dict]:
    return categories()


@app.get("/api/system")
def system_information() -> dict:
    disk = shutil.disk_usage(PROJECT_DIR)
    return {
        "platform": platform.system(), "release": platform.release(), "machine": platform.machine(),
        "processor_count": os.cpu_count() or 1,
        "disk_total_gb": round(disk.total / 1024**3, 1),
        "disk_free_gb": round(disk.free / 1024**3, 1),
        "local_time": datetime.now().astimezone().isoformat(),
    }


@app.post("/api/command", response_model=CommandResponse)
def command(payload: CommandRequest) -> CommandResponse:
    return CommandResponse(**route_command(payload.command).to_dict())


@app.post("/api/commands/batch", response_model=list[CommandResponse])
def command_batch(payload: BatchCommandRequest) -> list[CommandResponse]:
    return [CommandResponse(**route_command(item).to_dict()) for item in payload.commands if item.strip()]


@app.get("/api/history")
def command_history(limit: int = 20) -> list[dict]:
    return history.recent(max(1, min(limit, 100)))


@app.delete("/api/history", status_code=204)
def clear_command_history() -> None:
    history.clear()


@app.get("/api/memory")
def memories() -> dict:
    return load_memory()


@app.put("/api/memory")
def save_memory(payload: MemoryRequest) -> dict:
    remember(payload.key.strip().casefold(), payload.value.strip())
    return {"saved": True, "key": payload.key.strip().casefold()}


@app.delete("/api/memory/{key}")
def delete_memory(key: str) -> dict:
    return {"deleted": forget(key.strip().casefold())}


@app.get("/api/browser-data")
def local_browser_data(limit: int = 30) -> list[dict]:
    return browser_data.recent(max(1, min(limit, 100)))


@app.post("/api/wake", response_model=CommandResponse)
def wake() -> CommandResponse:
    reply = "Hi Sir"
    history.add("Hi Jarvis", reply, "wake")
    return CommandResponse(reply=reply)


frontend_dist = Path(__file__).parent / "frontend" / "dist"
app.mount("/generated", StaticFiles(directory=GENERATED_IMAGE_DIR), name="generated-images")
if frontend_dist.exists():
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="frontend")
