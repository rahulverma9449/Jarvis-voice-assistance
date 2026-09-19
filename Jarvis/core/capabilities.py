"""Discoverable Jarvis capability catalogue used by both the API and UI."""

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class Capability:
    id: str
    category: str
    title: str
    example: str
    description: str
    icon: str = "spark"

    def to_dict(self) -> dict:
        return asdict(self)


def _items(category: str, icon: str, rows: list[tuple[str, str, str]]) -> list[Capability]:
    return [
        Capability(f"{category.lower().replace(' ', '-')}-{index:02}", category, title, example, description, icon)
        for index, (title, example, description) in enumerate(rows, 1)
    ]


_WEB_SITES = [
    "Google", "YouTube", "Gmail", "GitHub", "LinkedIn", "Amazon", "Flipkart", "Netflix",
    "Spotify", "Reddit", "Stack Overflow", "Wikipedia", "Google Drive", "Google Maps",
    "Google Calendar", "ChatGPT", "Claude", "Gemini", "Canva", "Figma", "Notion", "Discord",
    "WhatsApp", "Instagram", "X",
]
_APPS = [
    "Notepad", "Calculator", "Paint", "File Explorer", "Settings", "Task Manager", "Terminal",
    "PowerShell", "Command Prompt", "VS Code", "Word", "Excel", "PowerPoint", "Camera", "Snipping Tool",
]
_SEARCHES = [
    "latest technology news", "Python tutorials", "nearby restaurants", "today's headlines",
    "machine learning roadmap", "interview questions", "healthy recipes", "travel destinations",
    "open source projects", "online courses", "stock market news", "weather forecast",
]

CAPABILITIES: list[Capability] = []
CAPABILITIES += _items("Web & Search", "globe", [
    (f"Open {site}", f"Open {site}", f"Launch {site} in a new browser tab.") for site in _WEB_SITES
])
CAPABILITIES += _items("Desktop", "desktop", [
    (f"Open {app}", f"Open {app}", f"Launch {app} safely on this computer.") for app in _APPS
])
CAPABILITIES += _items("Smart Search", "search", [
    (f"Search {term.title()}", f"Search for {term}", f"Search the web for {term}.") for term in _SEARCHES
])
CAPABILITIES += _items("AI Assistant", "brain", [
    ("Ask anything", "Explain quantum computing simply", "Answer a general question using the configured AI provider."),
    ("Summarize", "Summarize how neural networks work", "Create a concise summary."),
    ("Brainstorm", "Brainstorm names for my new app", "Generate creative ideas."),
    ("Write email", "Write a professional follow-up email", "Draft an email in your preferred tone."),
    ("Improve writing", "Improve this sentence: we need it fast", "Rewrite text for clarity."),
    ("Create checklist", "Create a launch checklist for a website", "Turn a goal into actionable steps."),
    ("Explain code", "Explain Python decorators", "Explain programming concepts."),
    ("Debug help", "Why does a Python KeyError happen?", "Diagnose a technical problem."),
    ("Compare", "Compare React and Vue", "Compare options and trade-offs."),
    ("Translate", "Translate hello, how are you to Hindi", "Translate natural-language text."),
])
CAPABILITIES += _items("Productivity", "check", [
    ("Save note", "Take a note buy groceries", "Save a note locally."),
    ("Read notes", "Read my notes", "Read your latest saved notes."),
    ("Command history", "Show my last 5 commands", "Review recent Jarvis activity."),
    ("Remember detail", "Remember that my favorite color is blue", "Store a personal detail locally."),
    ("Recall detail", "What do you remember about favorite color", "Recall saved information."),
    ("Start timer", "Set a timer for 5 minutes", "Start a countdown in the dashboard."),
    ("Start focus", "Start focus mode", "Open a focused study roadmap."),
    ("Study Python", "Start Python study mode", "Start a guided learning search."),
    ("Interview prep", "Start interview mode", "Open interview preparation resources."),
    ("Create image", "Generate image of a futuristic city", "Generate an AI image."),
    ("Scan food", "Scan food", "Open the camera scanner."),
    ("Take screenshot", "Take a screenshot", "Capture the current desktop."),
])
CAPABILITIES += _items("Math & Tools", "calculator", [
    ("Calculate", "Calculate 125 * 48", "Safely evaluate arithmetic."),
    ("Square root", "Calculate square root of 144", "Calculate a square root."),
    ("Percentage", "Calculate 18 percent of 950", "Calculate a percentage."),
    ("Kilometres to miles", "Convert 10 kilometers to miles", "Convert distance units."),
    ("Miles to kilometres", "Convert 5 miles to kilometers", "Convert distance units."),
    ("Celsius to Fahrenheit", "Convert 32 celsius to fahrenheit", "Convert temperatures."),
    ("Fahrenheit to Celsius", "Convert 90 fahrenheit to celsius", "Convert temperatures."),
    ("Kilograms to pounds", "Convert 70 kilograms to pounds", "Convert weight units."),
    ("Pounds to kilograms", "Convert 150 pounds to kilograms", "Convert weight units."),
    ("Metres to feet", "Convert 2 meters to feet", "Convert length units."),
    ("Uppercase text", "Uppercase hello Jarvis", "Transform text to uppercase."),
    ("Count words", "Count words Jarvis makes work easier", "Count words and characters."),
])
CAPABILITIES += _items("Media", "play", [
    ("Play music", "Play music Believer", "Find a song on YouTube Music."),
    ("Play YouTube", "Play Imagine Dragons on YouTube", "Find and play a YouTube video."),
    ("Search YouTube", "Search YouTube for React tutorial", "Open YouTube search results."),
    ("Play local song", "Play local song", "Play audio from your Music folder."),
    ("Play local video", "Play local video", "Play video from your Videos folder."),
    ("Pause", "Pause music", "Pause the active media session."),
    ("Resume", "Resume music", "Resume active media."),
    ("Next", "Next song", "Skip to the next track."),
    ("Previous", "Previous song", "Return to the previous track."),
    ("Volume up", "Volume up", "Increase system volume."),
    ("Volume down", "Volume down", "Decrease system volume."),
    ("Mute", "Mute", "Toggle system audio mute."),
])
CAPABILITIES += _items("System", "pulse", [
    ("System status", "System status", "Report the operating system."),
    ("Computer health", "Check computer health", "Report CPU, memory, and disk information."),
    ("CPU", "Check CPU", "Report processor utilization."),
    ("Memory", "Check RAM", "Report memory utilization."),
    ("Disk", "Check disk", "Report free disk capacity."),
    ("Current time", "What time is it", "Read the local time."),
    ("Current date", "What is today's date", "Read the local date."),
    ("Weather", "What is the weather in Delhi", "Get a current weather summary."),
    ("Tell joke", "Tell me a joke", "Tell a programming-friendly joke."),
    ("Restart safety", "Restart computer", "Explain protected power controls."),
    ("Shutdown safety", "Shutdown computer", "Explain protected power controls."),
    ("API health", "Is Jarvis online", "Check assistant health."),
])
CAPABILITIES += _items("Developer", "code", [
    ("Open VS Code", "Open VS Code", "Launch Visual Studio Code."),
    ("Open Python docs", "Open Python docs", "Open official Python documentation."),
    ("Open PyPI", "Open PyPI", "Browse Python packages."),
    ("Open GitHub", "Open GitHub", "Open GitHub."),
    ("Open Stack Overflow", "Open Stack Overflow", "Open Stack Overflow."),
    ("Create Python file", "Create Python file demo.py", "Create a Python source file."),
    ("Run Jarvis", "Run jarvis.py", "Start the desktop assistant."),
    ("Open requirements", "Open requirements.txt", "Open project dependencies."),
    ("Install package", "Install Python package requests", "Install one validated package."),
    ("Python tutorial", "Search Python tutorial", "Find Python learning material."),
    ("Git tutorial", "Search Git tutorial", "Find Git learning material."),
    ("API design", "Explain REST API design", "Ask AI about API architecture."),
])
CAPABILITIES += _items("Work & Atlassian", "work", [
    ("Open Jira", "Open Jira", "Open the configured Jira workspace."),
    ("Open Confluence", "Open Confluence", "Open the configured Confluence workspace."),
    ("Active sprint", "Check active sprint", "Summarize the active sprint."),
    ("Read Jira issue", "Read Jira JUG-12", "Read a Jira issue summary."),
    ("Update Jira status", "Update Jira JUG-12 status to done", "Transition a Jira issue."),
    ("Update Jira summary", "Update Jira JUG-12 summary to fix login", "Change an issue summary."),
    ("Sprint goal", "Update sprint goal to ship version two", "Update the active sprint goal."),
    ("Find Confluence", "Search Confluence architecture", "Find and summarize a page."),
])


def capability_dicts(category: str | None = None, search: str | None = None) -> list[dict]:
    items = CAPABILITIES
    if category:
        items = [item for item in items if item.category.casefold() == category.casefold()]
    if search:
        needle = search.casefold()
        items = [item for item in items if needle in f"{item.title} {item.example} {item.description} {item.category}".casefold()]
    return [item.to_dict() for item in items]


def categories() -> list[dict]:
    names = dict.fromkeys(item.category for item in CAPABILITIES)
    return [{"name": name, "count": sum(item.category == name for item in CAPABILITIES)} for name in names]
