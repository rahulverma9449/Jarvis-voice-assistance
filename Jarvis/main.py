from Jarvis.config import ASSISTANT_NAME, USER_NAME
from Jarvis.core.command_router import route_command
from Jarvis.core.speech import speech


def run() -> None:
    greeting = f"{ASSISTANT_NAME} online. Welcome back, {USER_NAME}."
    print(greeting)
    speech.speak(greeting)
    while True:
        command = speech.listen()
        if not command:
            continue
        print(f"You: {command}")
        if command in {"exit", "quit", "go offline"}:
            speech.speak("Going offline.")
            break
        result = route_command(command)
        print(f"{ASSISTANT_NAME}: {result.reply}")
        speech.speak(result.reply)


if __name__ == "__main__":
    run()
