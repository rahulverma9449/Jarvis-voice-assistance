import requests

from Jarvis.config import WEATHER_CITY


def get_weather(query: str) -> tuple[str, str, str | None]:
    city = query.replace("weather", "").replace("in", "", 1).strip() or WEATHER_CITY
    try:
        response = requests.get(f"https://wttr.in/{city}", params={"format": "j1"}, timeout=6)
        response.raise_for_status()
        current = response.json()["current_condition"][0]
        description = current["weatherDesc"][0]["value"]
        reply = f"It is {current['temp_C']} degrees Celsius and {description.lower()} in {city}."
        return reply, "speak", None
    except (requests.RequestException, KeyError, IndexError, ValueError):
        return "I couldn't retrieve the weather right now.", "speak", None
