import pyttsx3
import speech_recognition as sr

from Jarvis.config import LANGUAGE, VOICE_RATE


class SpeechService:
    def __init__(self) -> None:
        self._engine = None

    def _get_engine(self):
        if self._engine is None:
            self._engine = pyttsx3.init()
            voices = self._engine.getProperty("voices")
            if voices:
                self._engine.setProperty("voice", voices[min(1, len(voices) - 1)].id)
            self._engine.setProperty("rate", VOICE_RATE)
        return self._engine

    def speak(self, text: str) -> None:
        engine = self._get_engine()
        engine.say(text)
        engine.runAndWait()

    def listen(self, timeout: int = 5) -> str | None:
        recognizer = sr.Recognizer()
        recognizer.pause_threshold = 0.55
        recognizer.phrase_threshold = 0.2
        recognizer.non_speaking_duration = 0.2
        with sr.Microphone() as source:
            print("Listening...")
            recognizer.adjust_for_ambient_noise(source, duration=0.2)
            try:
                audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=8)
            except sr.WaitTimeoutError:
                return None
        try:
            return recognizer.recognize_google(audio, language=LANGUAGE).lower()
        except (sr.UnknownValueError, sr.RequestError):
            return None


speech = SpeechService()
