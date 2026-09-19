import datetime
import json
import os
import random
import subprocess
import time
import urllib.parse
import webbrowser
from pathlib import Path

import pyautogui
import pyjokes
import pyttsx3
import speech_recognition as sr
import wikipedia

try:
    import pywhatkit
except ImportError:
    pywhatkit = None


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

HISTORY_FILE = DATA_DIR / "history.jsonl"
NAME_FILE = DATA_DIR / "assistant_name.txt"

SCREENSHOT_DIR = DATA_DIR / "screenshots"
SCREENSHOT_DIR.mkdir(exist_ok=True)

MUSIC_DIR = Path.home() / "Music"

WAKE_WORDS = [
    "hello jarvis",
    "hey jarvis",
    "hi jarvis",
    "jarvis",
]

SLEEP_COMMANDS = [
    "go to sleep",
    "sleep",
    "stop listening",
]

EXIT_COMMANDS = [
    "offline",
    "exit jarvis",
    "close jarvis",
    "goodbye jarvis",
]


# ============================================================
# TEXT TO SPEECH
# ============================================================

engine = pyttsx3.init()

voices = engine.getProperty("voices")

if len(voices) > 1:
    engine.setProperty("voice", voices[1].id)
elif voices:
    engine.setProperty("voice", voices[0].id)

engine.setProperty("rate", 165)
engine.setProperty("volume", 1.0)


def speak(text: str) -> None:
    """Convert text to speech."""

    if not text:
        return

    print(f"Jarvis: {text}")

    try:
        engine.say(text)
        engine.runAndWait()

    except Exception as error:
        print("Speech error:", error)


# ============================================================
# HISTORY
# ============================================================

def save_history(command: str, response: str = "") -> None:
    """Store command history inside data/history.jsonl."""

    record = {
        "timestamp": datetime.datetime.now().isoformat(
            timespec="seconds"
        ),
        "command": command,
        "response": response,
    }

    try:
        with open(
            HISTORY_FILE,
            "a",
            encoding="utf-8"
        ) as file:

            file.write(
                json.dumps(
                    record,
                    ensure_ascii=False
                ) + "\n"
            )

    except Exception as error:
        print("History saving error:", error)


def show_history(limit: int = 10) -> None:
    """Display recent command history."""

    if not HISTORY_FILE.exists():
        speak("There is no command history yet.")
        return

    try:
        with open(
            HISTORY_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            lines = file.readlines()

        if not lines:
            speak("History is empty.")
            return

        recent = lines[-limit:]

        print("\n========== JARVIS HISTORY ==========\n")

        for line in recent:

            data = json.loads(line)

            print("Time:", data.get("timestamp"))
            print("Command:", data.get("command"))
            print("Response:", data.get("response"))
            print("-" * 50)

        speak(f"Showing your last {len(recent)} commands.")

    except Exception as error:
        print(error)
        speak("I couldn't read the history.")


def clear_history() -> None:
    """Clear command history."""

    try:

        HISTORY_FILE.write_text("", encoding="utf-8")

        speak("Command history has been cleared.")

    except Exception:
        speak("I couldn't clear the history.")


# ============================================================
# ASSISTANT NAME
# ============================================================

def load_name() -> str:

    try:

        if NAME_FILE.exists():

            name = NAME_FILE.read_text(
                encoding="utf-8"
            ).strip()

            return name or "Jarvis"

    except Exception:
        pass

    return "Jarvis"


def set_name() -> None:

    speak("What would you like to name me?")

    name = listen(timeout=7)

    if name:

        NAME_FILE.write_text(
            name.title(),
            encoding="utf-8"
        )

        speak(
            f"Alright sir. "
            f"From now on you can call me {name}."
        )

    else:
        speak("I could not hear the name.")


# ============================================================
# SPEECH RECOGNITION
# ============================================================

recognizer = sr.Recognizer()

recognizer.dynamic_energy_threshold = True
recognizer.pause_threshold = 0.8


def listen(
    timeout: int = 5,
    phrase_time_limit: int = 8
) -> str | None:

    """Listen from microphone."""

    try:

        with sr.Microphone() as source:

            print("\nListening...")

            recognizer.adjust_for_ambient_noise(
                source,
                duration=0.4
            )

            audio = recognizer.listen(
                source,
                timeout=timeout,
                phrase_time_limit=phrase_time_limit,
            )

        print("Recognizing...")

        query = recognizer.recognize_google(
            audio,
            language="en-IN"
        )

        query = query.lower().strip()

        print(f"You: {query}")

        return query

    except sr.WaitTimeoutError:
        return None

    except sr.UnknownValueError:
        return None

    except sr.RequestError:

        speak(
            "Speech recognition service "
            "is currently unavailable."
        )

        return None

    except Exception as error:

        print("Microphone error:", error)

        return None


# ============================================================
# GREETING
# ============================================================

def wish_me() -> None:

    name = load_name()

    hour = datetime.datetime.now().hour

    if 5 <= hour < 12:
        greeting = "Good morning"

    elif 12 <= hour < 17:
        greeting = "Good afternoon"

    elif 17 <= hour < 22:
        greeting = "Good evening"

    else:
        greeting = "Hello"

    speak(
        f"{greeting}, sir. "
        f"{name} is running in the background."
    )

    speak(
        f"Just say Hello {name} whenever you need me."
    )


# ============================================================
# TIME AND DATE
# ============================================================

def tell_time() -> None:

    current_time = datetime.datetime.now().strftime(
        "%I:%M %p"
    )

    response = f"The current time is {current_time}."

    speak(response)

    save_history("time", response)


def tell_date() -> None:

    today = datetime.datetime.now()

    current_date = today.strftime(
        "%A, %d %B %Y"
    )

    response = f"Today is {current_date}."

    speak(response)

    save_history("date", response)


# ============================================================
# SCREENSHOT
# ============================================================

def take_screenshot() -> None:

    try:

        timestamp = datetime.datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )

        filename = SCREENSHOT_DIR / (
            f"screenshot_{timestamp}.png"
        )

        image = pyautogui.screenshot()

        image.save(filename)

        response = (
            f"Screenshot taken and saved "
            f"inside the data screenshots folder."
        )

        speak(response)

        print("Saved:", filename)

        save_history("screenshot", response)

    except Exception as error:

        print(error)

        speak("I couldn't take the screenshot.")


# ============================================================
# WIKIPEDIA
# ============================================================

def search_wikipedia(topic: str) -> None:

    if not topic:

        speak("What should I search on Wikipedia?")
        topic = listen()

    if not topic:
        return

    try:

        speak(f"Searching Wikipedia for {topic}.")

        result = wikipedia.summary(
            topic,
            sentences=3,
            auto_suggest=True
        )

        print("\nWikipedia:")
        print(result)

        speak(result)

        save_history(
            f"wikipedia {topic}",
            result
        )

    except wikipedia.exceptions.DisambiguationError as error:

        options = error.options[:5]

        print("Possible results:", options)

        speak(
            "I found multiple results. "
            "Please be more specific."
        )

    except wikipedia.exceptions.PageError:

        speak("I could not find that topic on Wikipedia.")

    except Exception as error:

        print(error)

        speak("Wikipedia search failed.")


# ============================================================
# GOOGLE SEARCH
# ============================================================

def google_search(search_query: str) -> None:

    if not search_query:

        speak("What should I search for?")
        search_query = listen()

    if not search_query:
        return

    encoded = urllib.parse.quote_plus(search_query)

    url = f"https://www.google.com/search?q={encoded}"

    webbrowser.open(url)

    response = f"Searching Google for {search_query}."

    speak(response)

    save_history(
        f"google {search_query}",
        response
    )


# ============================================================
# YOUTUBE
# ============================================================

def youtube_search(search_query: str) -> None:

    if not search_query:

        speak("What should I search on YouTube?")
        search_query = listen()

    if not search_query:
        return

    encoded = urllib.parse.quote_plus(search_query)

    url = (
        "https://www.youtube.com/results"
        f"?search_query={encoded}"
    )

    webbrowser.open(url)

    response = (
        f"Searching YouTube for {search_query}."
    )

    speak(response)

    save_history(
        f"youtube search {search_query}",
        response
    )


def play_youtube(search_query: str) -> None:
    """
    Play first YouTube result using pywhatkit.
    Falls back to YouTube search.
    """

    if not search_query:

        search_query = "popular music"

    speak(
        f"Playing {search_query} on YouTube."
    )

    try:

        if pywhatkit:

            pywhatkit.playonyt(search_query)

        else:

            youtube_search(search_query)

        save_history(
            f"play {search_query}",
            f"Playing {search_query} on YouTube"
        )

    except Exception as error:

        print("YouTube error:", error)

        youtube_search(search_query)


# ============================================================
# LOCAL MUSIC
# ============================================================

AUDIO_EXTENSIONS = {
    ".mp3",
    ".wav",
    ".m4a",
    ".aac",
    ".flac",
    ".ogg",
}


def get_local_songs():
    """Get songs recursively from Music directory."""

    if not MUSIC_DIR.exists():
        return []

    songs = []

    for file in MUSIC_DIR.rglob("*"):

        if (
            file.is_file()
            and file.suffix.lower() in AUDIO_EXTENSIONS
        ):
            songs.append(file)

    return songs


def play_local_music(search_term: str = "") -> bool:
    """
    Search and play local songs.
    """

    songs = get_local_songs()

    if not songs:
        return False

    if search_term:

        keywords = search_term.lower().split()

        matching = []

        for song in songs:

            song_name = song.stem.lower()

            if any(
                word in song_name
                for word in keywords
            ):
                matching.append(song)

        songs = matching

    if not songs:
        return False

    selected_song = random.choice(songs)

    try:

        os.startfile(str(selected_song))

        response = (
            f"Playing {selected_song.stem} "
            f"from your computer."
        )

        speak(response)

        save_history(
            f"local music {search_term}",
            response
        )

        return True

    except Exception as error:

        print("Music error:", error)

        return False


def play_music_command(command: str) -> None:
    """
    Intelligent music handler.

    Examples:
    play punjabi songs
    play hindi songs
    play arijit singh
    play mp3
    play local music
    """

    search_term = command.lower()

    replacements = [
        "play music",
        "play song",
        "play songs",
        "play",
        "on youtube",
        "youtube",
    ]

    for word in replacements:
        search_term = search_term.replace(
            word,
            ""
        )

    search_term = search_term.strip()

    # Local music request
    if any(
        word in command
        for word in [
            "local",
            "mp3",
            "computer",
            "my music",
            "offline music",
        ]
    ):

        local_query = search_term

        for word in [
            "local",
            "mp3",
            "computer",
            "offline",
            "my music",
        ]:
            local_query = local_query.replace(
                word,
                ""
            )

        local_query = local_query.strip()

        if play_local_music(local_query):
            return

        speak(
            "I couldn't find that song locally. "
            "I will search YouTube instead."
        )

    # Categories
    if "punjabi" in command:

        play_youtube(
            "latest Punjabi songs"
        )

    elif "hindi" in command:

        play_youtube(
            "latest Hindi Bollywood songs"
        )

    elif "bollywood" in command:

        play_youtube(
            "Bollywood hit songs"
        )

    elif "english" in command:

        play_youtube(
            "English hit songs"
        )

    elif "romantic" in command:

        play_youtube(
            "Hindi romantic songs"
        )

    elif "party" in command:

        play_youtube(
            "party songs"
        )

    elif "sad" in command:

        play_youtube(
            "Hindi sad songs"
        )

    elif "workout" in command:

        play_youtube(
            "workout music"
        )

    elif "relaxing" in command:

        play_youtube(
            "relaxing music"
        )

    elif search_term:

        play_youtube(search_term)

    else:

        play_youtube(
            "latest Hindi songs"
        )


# ============================================================
# OPEN WEBSITES
# ============================================================

WEBSITES = {

    "youtube": "https://www.youtube.com",

    "google": "https://www.google.com",

    "gmail": "https://mail.google.com",

    "github": "https://github.com",

    "linkedin": "https://www.linkedin.com",

    "instagram": "https://www.instagram.com",

    "facebook": "https://www.facebook.com",

    "whatsapp": "https://web.whatsapp.com",

    "chatgpt": "https://chatgpt.com",

    "stackoverflow": "https://stackoverflow.com",

    "amazon": "https://www.amazon.in",

    "flipkart": "https://www.flipkart.com",
}


def open_website(command: str) -> bool:

    for website, url in WEBSITES.items():

        if website in command:

            speak(f"Opening {website}.")

            webbrowser.open(url)

            save_history(
                command,
                f"Opened {website}"
            )

            return True

    return False


# ============================================================
# WINDOWS APPLICATIONS
# ============================================================

APPLICATIONS = {

    "notepad": "notepad.exe",

    "calculator": "calc.exe",

    "paint": "mspaint.exe",

    "command prompt": "cmd.exe",

    "cmd": "cmd.exe",

    "powershell": "powershell.exe",

    "explorer": "explorer.exe",
}


def open_application(command: str) -> bool:

    for app_name, executable in APPLICATIONS.items():

        if app_name in command:

            try:

                subprocess.Popen(executable)

                speak(f"Opening {app_name}.")

                save_history(
                    command,
                    f"Opened {app_name}"
                )

                return True

            except Exception as error:

                print(error)

                speak(
                    f"I couldn't open {app_name}."
                )

                return True

    return False


# ============================================================
# VOLUME
# ============================================================

def volume_control(command: str) -> bool:

    if (
        "volume up" in command
        or "increase volume" in command
    ):

        pyautogui.press(
            "volumeup",
            presses=5
        )

        speak("Volume increased.")

        return True

    if (
        "volume down" in command
        or "decrease volume" in command
    ):

        pyautogui.press(
            "volumedown",
            presses=5
        )

        speak("Volume decreased.")

        return True

    if (
        "mute" in command
        or "unmute" in command
    ):

        pyautogui.press(
            "volumemute"
        )

        speak("Volume toggled.")

        return True

    return False


# ============================================================
# KEYBOARD AUTOMATION
# ============================================================

def typing_command(command: str) -> bool:

    if command.startswith("type "):

        text = command.removeprefix(
            "type "
        ).strip()

        if text:

            speak("Typing.")

            pyautogui.write(
                text,
                interval=0.05
            )

            save_history(
                command,
                f"Typed: {text}"
            )

        return True

    return False


# ============================================================
# SYSTEM ACTIONS
# ============================================================

def confirm_action(action: str) -> bool:

    speak(
        f"Are you sure you want me to {action}?"
    )

    answer = listen(
        timeout=5,
        phrase_time_limit=4
    )

    if answer and any(
        confirmation in answer
        for confirmation in [
            "yes",
            "sure",
            "confirm",
            "do it",
        ]
    ):

        return True

    speak(f"{action.capitalize()} cancelled.")

    return False


def shutdown_pc() -> None:

    if confirm_action("shutdown the computer"):

        speak("Shutting down the computer. Goodbye sir.")

        os.system(
            "shutdown /s /f /t 5"
        )


def restart_pc() -> None:

    if confirm_action("restart the computer"):

        speak("Restarting the computer.")

        os.system(
            "shutdown /r /f /t 5"
        )


# ============================================================
# JOKE
# ============================================================

def tell_joke() -> None:

    joke = pyjokes.get_joke()

    print(joke)

    speak(joke)

    save_history(
        "tell me a joke",
        joke
    )


# ============================================================
# MAIN COMMAND PROCESSOR
# ============================================================

def process_command(query: str) -> str:
    """
    Main brain of Jarvis.

    Return:
        sleep -> go back to wake mode
        exit  -> completely close Jarvis
        active -> continue listening
    """

    if not query:
        return "active"

    save_history(query)

    # ------------------------------------------------
    # Exit
    # ------------------------------------------------

    if any(
        command in query
        for command in EXIT_COMMANDS
    ):

        speak(
            "Going offline. Have a great day sir."
        )

        return "exit"

    # ------------------------------------------------
    # Sleep
    # ------------------------------------------------

    if any(
        command in query
        for command in SLEEP_COMMANDS
    ):

        speak(
            "Alright sir. "
            "Call me whenever you need me."
        )

        return "sleep"

    # ------------------------------------------------
    # Time
    # ------------------------------------------------

    if (
        "time" in query
        and "timer" not in query
    ):

        tell_time()

    # ------------------------------------------------
    # Date
    # ------------------------------------------------

    elif (
        "date" in query
        or "what day is it" in query
    ):

        tell_date()

    # ------------------------------------------------
    # Wikipedia
    # ------------------------------------------------

    elif "wikipedia" in query:

        topic = (
            query.replace(
                "wikipedia",
                ""
            )
            .replace(
                "search",
                ""
            )
            .strip()
        )

        search_wikipedia(topic)

    # ------------------------------------------------
    # Google search
    # ------------------------------------------------

    elif (
        query.startswith("search google")
        or query.startswith("google search")
        or query.startswith("search for")
    ):

        search_query = query

        phrases = [
            "search google for",
            "search google",
            "google search for",
            "google search",
            "search for",
        ]

        for phrase in phrases:
            search_query = search_query.replace(
                phrase,
                ""
            )

        google_search(
            search_query.strip()
        )

    # ------------------------------------------------
    # YouTube search
    # ------------------------------------------------

    elif (
        "search youtube" in query
        or "youtube search" in query
    ):

        search_query = (
            query.replace(
                "search youtube",
                ""
            )
            .replace(
                "youtube search",
                ""
            )
            .replace(
                "for",
                ""
            )
            .strip()
        )

        youtube_search(
            search_query
        )

    # ------------------------------------------------
    # Music
    # ------------------------------------------------

    elif any(
        word in query
        for word in [
            "play music",
            "play song",
            "play songs",
            "play punjabi",
            "play hindi",
            "play bollywood",
            "play english",
            "play romantic",
            "play sad",
            "play party",
            "play workout",
            "play mp3",
            "play local",
        ]
    ) or query.startswith("play "):

        play_music_command(query)

    # ------------------------------------------------
    # Open website
    # ------------------------------------------------

    elif query.startswith("open "):

        if open_website(query):
            pass

        elif open_application(query):
            pass

        else:

            website = (
                query.replace(
                    "open",
                    ""
                )
                .strip()
                .replace(" ", "")
            )

            speak(
                f"I will search for {website}."
            )

            google_search(website)

    # ------------------------------------------------
    # Screenshot
    # ------------------------------------------------

    elif (
        "screenshot" in query
        or "take screen shot" in query
    ):

        take_screenshot()

    # ------------------------------------------------
    # Joke
    # ------------------------------------------------

    elif (
        "joke" in query
        or "make me laugh" in query
    ):

        tell_joke()

    # ------------------------------------------------
    # Volume
    # ------------------------------------------------

    elif volume_control(query):
        pass

    # ------------------------------------------------
    # Type
    # ------------------------------------------------

    elif typing_command(query):
        pass

    # ------------------------------------------------
    # Name
    # ------------------------------------------------

    elif (
        "change your name" in query
        or "rename yourself" in query
    ):

        set_name()

    elif (
        "what is your name" in query
        or "who are you" in query
    ):

        assistant_name = load_name()

        speak(
            f"My name is {assistant_name}, sir."
        )

    # ------------------------------------------------
    # History
    # ------------------------------------------------

    elif (
        "show history" in query
        or "command history" in query
    ):

        show_history()

    elif "clear history" in query:

        if confirm_action(
            "clear your command history"
        ):

            clear_history()

    # ------------------------------------------------
    # Shutdown
    # ------------------------------------------------

    elif "shutdown" in query:

        shutdown_pc()

    # ------------------------------------------------
    # Restart
    # ------------------------------------------------

    elif "restart" in query:

        restart_pc()

    # ------------------------------------------------
    # Greetings
    # ------------------------------------------------

    elif any(
        greeting in query
        for greeting in [
            "how are you",
            "are you there",
        ]
    ):

        speak(
            "I am doing great sir. "
            "I am ready to help you."
        )

    elif (
        "thank you" in query
        or "thanks jarvis" in query
    ):

        speak(
            "You're welcome sir. "
            "Always happy to help."
        )

    # ------------------------------------------------
    # Unknown command
    # ------------------------------------------------

    else:

        speak(
            "I don't have a dedicated command "
            "for that yet. "
            "Would you like me to search Google?"
        )

        answer = listen(
            timeout=5,
            phrase_time_limit=4
        )

        if answer and "yes" in answer:

            google_search(query)

        else:

            speak("Alright sir.")

    return "active"


# ============================================================
# WAKE WORD MODE
# ============================================================

def wait_for_wake_word() -> bool:
    """
    Jarvis stays sleeping until wake phrase is detected.
    """

    print("\n===================================")
    print("      JARVIS SLEEPING MODE")
    print("===================================")
    print("Say: Hello Jarvis")
    print("===================================\n")

    while True:

        query = listen(
            timeout=5,
            phrase_time_limit=5
        )

        if not query:
            continue

        # Exit even from sleeping mode
        if any(
            command in query
            for command in EXIT_COMMANDS
        ):

            speak("Goodbye sir.")

            return False

        # Wake word
        if any(
            wake_word in query
            for wake_word in WAKE_WORDS
        ):

            speak("Yes sir, I am here.")

            return True


# ============================================================
# ACTIVE MODE
# ============================================================

def active_mode() -> bool:

    speak("What can I do for you?")

    while True:

        query = listen(
            timeout=8,
            phrase_time_limit=10
        )

        if not query:
            continue

        result = process_command(query)

        if result == "exit":
            return False

        if result == "sleep":
            return True

        # Optional:
        # Automatically sleep after every command.
        #
        # Uncomment these lines if you want:
        #
        # speak("Anything else sir?")
        # return True


# ============================================================
# MAIN
# ============================================================

def main():

    print(
        r"""
     ██╗ █████╗ ██████╗ ██╗   ██╗██╗███████╗
     ██║██╔══██╗██╔══██╗██║   ██║██║██╔════╝
     ██║███████║██████╔╝██║   ██║██║███████╗
██   ██║██╔══██║██╔══██╗╚██╗ ██╔╝██║╚════██║
╚█████╔╝██║  ██║██║  ██║ ╚████╔╝ ██║███████║
 ╚════╝ ╚═╝  ╚═╝╚═╝  ╚═╝  ╚═══╝  ╚═╝╚══════╝

          PERSONAL AI ASSISTANT
"""
    )

    wish_me()

    while True:

        awakened = wait_for_wake_word()

        if not awakened:
            break

        should_continue = active_mode()

        if not should_continue:
            break


if __name__ == "__main__":
    main()