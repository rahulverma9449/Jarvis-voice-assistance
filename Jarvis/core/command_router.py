from dataclasses import asdict, dataclass
from datetime import datetime
import re
from typing import Callable

from Jarvis.ai.llm import ask_ai
from Jarvis.core.browser_datastore import browser_data
from Jarvis.core.history import history
from Jarvis.core.wake_word import strip_wake_word
from Jarvis.skills.apps import is_app_or_folder, open_app
from Jarvis.skills.atlassian import active_sprint, open_atlassian, read_confluence, read_jira_issue, update_jira, update_sprint
from Jarvis.skills.browser import browser_command
from Jarvis.skills.developer import developer_command, is_developer_command
from Jarvis.skills.food_scanner import scan_food
from Jarvis.skills.jokes import tell_joke
from Jarvis.skills.image_generation import generate_image
from Jarvis.skills.local_media import is_local_media_command, play_local_media
from Jarvis.skills.music import play_music
from Jarvis.skills.productivity import notes_command, show_history, study_mode
from Jarvis.skills.screenshot import take_screenshot
from Jarvis.skills.system import computer_health, media_control, protected_power_action, system_status
from Jarvis.skills.weather import get_weather
from Jarvis.skills.wikipedia_skill import search_wikipedia
from Jarvis.skills.youtube import youtube_command
from Jarvis.skills.utilities import is_utility_command, utility_command
from Jarvis.skills.memory_skill import is_memory_command, memory_command
from Jarvis.skills.web_shortcuts import is_website_command, open_website, search_web


SkillResult = tuple[str, str, str | None]
SkillHandler = Callable[[str], SkillResult]


@dataclass
class CommandResult:
    reply: str
    action: str = "speak"
    url: str | None = None

    def to_dict(self) -> dict:
        return asdict(self)


def _time(_: str) -> SkillResult:
    return f"The current time is {datetime.now():%I:%M %p}.", "speak", None


def _date(_: str) -> SkillResult:
    return f"Today is {datetime.now():%A, %d %B %Y}.", "speak", None


ROUTES: tuple[tuple[Callable[[str], bool], SkillHandler], ...] = (
    (lambda q: any(phrase in q for phrase in ("scan the products", "scan products", "scan food", "scan the food", "food scanner")), scan_food),
    (lambda q: "update sprint" in q, update_sprint),
    (lambda q: "check sprint" in q or "active sprint" in q, active_sprint),
    (lambda q: q.startswith("update jira"), update_jira),
    (lambda q: ("check jira" in q or "read jira" in q) and re.search(r"[a-z]+-\d+", q), read_jira_issue),
    (lambda q: q.startswith(("read confluence", "search confluence", "check confluence")), read_confluence),
    (lambda q: "open jira" in q or "open confluence" in q, open_atlassian),
    (lambda q: q.startswith(("generate image", "generate an image", "create image", "create an image", "draw ")), generate_image),
    (lambda q: q.startswith(("take a note", "create note", "write note", "save note", "read my notes", "show notes", "open notes")), notes_command),
    (is_memory_command, memory_command),
    (lambda q: ("history" in q or bool(re.search(r"show\s+last\s+\d+\s+commands", q))) and not q.startswith("clear "), show_history),
    (lambda q: q.startswith("start ") and ("study mode" in q or "interview" in q or "focus mode" in q or "coding mode" in q), study_mode),
    (is_utility_command, utility_command),
    (lambda q: "time" in q, _time),
    (lambda q: "date" in q or "day is it" in q, _date),
    (lambda q: "weather" in q, get_weather),
    (lambda q: "joke" in q, tell_joke),
    (lambda q: any(control in q for control in ("volume up", "volume down", "mute", "unmute", "pause music", "resume music", "stop music", "next song", "previous song")), media_control),
    (lambda q: any(metric in q for metric in ("check cpu", "check ram", "check disk", "computer health", "system information")), computer_health),
    (is_local_media_command, play_local_media),
    (is_developer_command, developer_command),
    (lambda q: "youtube" in q, youtube_command),
    (lambda q: q.startswith("play "), youtube_command),
    (is_website_command, open_website),
    (lambda q: q.startswith(("search ", "search for ", "google ")), search_web),
    (lambda q: "wikipedia" in q, search_wikipedia),
    (lambda q: q.startswith("search google for ") or "open google" in q, browser_command),
    (lambda q: "play music" in q or "play song" in q, play_music),
    (lambda q: "screenshot" in q, take_screenshot),
    (is_app_or_folder, open_app),
    (lambda q: q.startswith("open "), search_web),
    (lambda q: "system status" in q or "jarvis online" in q, system_status),
    (lambda q: "shutdown" in q or "restart" in q, protected_power_action),
)


def route_command(command: str) -> CommandResult:
    query, _ = strip_wake_word(command)
    if not query:
        result = CommandResult("I didn't hear a command.")
    else:
        result = None
        for matches, handler in ROUTES:
            if matches(query):
                result = CommandResult(*handler(query))
                break
        if result is None:
            result = CommandResult(ask_ai(query))
    history.add(command, result.reply, result.action)
    if "jira" in query or "sprint" in query or "confluence" in query:
        source = "confluence" if "confluence" in query else "jira"
        browser_data.add(source, command, result.reply, result.url)
    return result
