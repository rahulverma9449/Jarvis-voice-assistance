import re

import requests
from bs4 import BeautifulSoup

from Jarvis.config import ATLASSIAN_API_TOKEN, ATLASSIAN_EMAIL, ATLASSIAN_SITE_URL, JIRA_BOARD_ID


SkillResult = tuple[str, str, str | None]


def _configured(write: bool = False) -> bool:
    return bool(ATLASSIAN_SITE_URL and (not write or (ATLASSIAN_EMAIL and ATLASSIAN_API_TOKEN)))


def _request(method: str, path: str, **kwargs) -> requests.Response:
    response = requests.request(
        method,
        f"{ATLASSIAN_SITE_URL}{path}",
        auth=(ATLASSIAN_EMAIL, ATLASSIAN_API_TOKEN),
        headers={"Accept": "application/json", "Content-Type": "application/json"},
        timeout=20,
        **kwargs,
    )
    response.raise_for_status()
    return response


def _setup_message() -> SkillResult:
    return "Configure your Atlassian site, email, API token, and Jira board ID in the .env file first.", "speak", None


def open_atlassian(query: str) -> SkillResult:
    if not ATLASSIAN_SITE_URL:
        return "Opening the Atlassian application launcher. Configure your site URL for direct access.", "open_url", "https://start.atlassian.com"
    if "confluence" in query:
        return "Opening Confluence.", "open_url", f"{ATLASSIAN_SITE_URL}/wiki"
    return "Opening Jira.", "open_url", f"{ATLASSIAN_SITE_URL}/jira"


def active_sprint(_: str) -> SkillResult:
    if not (_configured(write=True) and JIRA_BOARD_ID):
        return _setup_message()
    try:
        sprints = _request("GET", f"/rest/agile/1.0/board/{JIRA_BOARD_ID}/sprint", params={"state": "active"}).json().get("values", [])
        if not sprints:
            return "There is no active sprint on the configured Jira board.", "speak", None
        sprint = sprints[0]
        issues = _request("GET", f"/rest/agile/1.0/sprint/{sprint['id']}/issue", params={"maxResults": 50, "fields": "summary,status,assignee"}).json().get("issues", [])
        done = sum(1 for issue in issues if issue.get("fields", {}).get("status", {}).get("statusCategory", {}).get("key") == "done")
        return f"{sprint['name']} is active with {len(issues)} issues. {done} are done and {len(issues) - done} remain.", "speak", None
    except (requests.RequestException, KeyError, IndexError, ValueError):
        return "I couldn't read the active Jira sprint. Check your Atlassian access and board ID.", "speak", None


def read_jira_issue(query: str) -> SkillResult:
    if not _configured(write=True):
        return _setup_message()
    match = re.search(r"\b([A-Z][A-Z0-9]+-\d+)\b", query.upper())
    if not match:
        return "Please say the Jira issue key, for example JUG-12.", "speak", None
    key = match.group(1)
    try:
        fields = _request("GET", f"/rest/api/3/issue/{key}", params={"fields": "summary,status,assignee"}).json()["fields"]
        assignee = (fields.get("assignee") or {}).get("displayName", "unassigned")
        return f"{key}: {fields['summary']}. Status {fields['status']['name']}, assigned to {assignee}.", "speak", None
    except (requests.RequestException, KeyError):
        return f"I couldn't read Jira issue {key}.", "speak", None


def update_jira(query: str) -> SkillResult:
    if not _configured(write=True):
        return _setup_message()
    issue = re.search(r"\b([A-Z][A-Z0-9]+-\d+)\b", query.upper())
    if not issue:
        return "Please include the Jira issue key you want to update.", "speak", None
    key = issue.group(1)
    status_match = re.search(r"status\s+to\s+(.+)$", query, re.IGNORECASE)
    summary_match = re.search(r"summary\s+to\s+(.+)$", query, re.IGNORECASE)
    try:
        if status_match:
            target = status_match.group(1).strip().lower()
            transitions = _request("GET", f"/rest/api/3/issue/{key}/transitions").json().get("transitions", [])
            transition = next((item for item in transitions if item["name"].lower() == target), None)
            if not transition:
                available = ", ".join(item["name"] for item in transitions[:5])
                return f"Status {target} is not available. Try {available}.", "speak", None
            _request("POST", f"/rest/api/3/issue/{key}/transitions", json={"transition": {"id": transition["id"]}})
            return f"Updated {key} status to {transition['name']}.", "speak", None
        if summary_match:
            summary = summary_match.group(1).strip()
            _request("PUT", f"/rest/api/3/issue/{key}", json={"fields": {"summary": summary}})
            return f"Updated the summary for {key}.", "speak", None
        return "Say update Jira, the issue key, and either status to or summary to followed by the new value.", "speak", None
    except (requests.RequestException, KeyError, StopIteration):
        return f"I couldn't update {key}. Check your Jira permissions and requested transition.", "speak", None


def update_sprint(query: str) -> SkillResult:
    if not (_configured(write=True) and JIRA_BOARD_ID):
        return _setup_message()
    goal_match = re.search(r"goal\s+to\s+(.+)$", query, re.IGNORECASE)
    if not goal_match:
        return "Say update sprint goal to, followed by the new goal.", "speak", None
    try:
        sprints = _request("GET", f"/rest/agile/1.0/board/{JIRA_BOARD_ID}/sprint", params={"state": "active"}).json().get("values", [])
        if not sprints:
            return "There is no active sprint to update.", "speak", None
        _request("POST", f"/rest/agile/1.0/sprint/{sprints[0]['id']}", json={"goal": goal_match.group(1).strip()})
        return f"Updated the goal for {sprints[0]['name']}.", "speak", None
    except (requests.RequestException, KeyError, IndexError):
        return "I couldn't update the active sprint goal.", "speak", None


def read_confluence(query: str) -> SkillResult:
    if not _configured(write=True):
        return _setup_message()
    term = re.sub(r"^(read|search|check)\s+confluence(?:\s+(?:for|page))?\s*", "", query, flags=re.IGNORECASE).strip()
    if not term:
        return "Tell me which Confluence topic to find.", "speak", None
    safe_term = term.replace('"', '\\"')
    try:
        result = _request("GET", "/wiki/rest/api/content/search", params={"cql": f'type=page AND text~"{safe_term}"', "limit": 1, "expand": "body.view"}).json().get("results", [])
        if not result:
            return f"I couldn't find a Confluence page about {term}.", "speak", None
        page = result[0]
        text = BeautifulSoup(page.get("body", {}).get("view", {}).get("value", ""), "html.parser").get_text(" ", strip=True)
        summary = text[:500] or "The page has no readable text."
        url = f"{ATLASSIAN_SITE_URL}/wiki{page.get('_links', {}).get('webui', '')}"
        return f"{page['title']}. {summary}", "open_url", url
    except (requests.RequestException, KeyError, IndexError):
        return "I couldn't read Confluence. Check your Atlassian access.", "speak", None
