# voice_processing.py
import speech_recognition as sr
import pyttsx3
import logging
import threading
import time

logger = logging.getLogger(__name__)

class VoiceProcessor:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.tts_engine = pyttsx3.init()
        self.speak_lock = threading.Lock()

    def listen_for_voice_command(self):
        """Continuous voice command listening thread."""
        while True:
            try:
                with self.microphone as source:
                    logger.info("Listening for command...")
                    self.recognizer.adjust_for_ambient_noise(source)
                    audio = self.recognizer.listen(source)
            
                try:
                    command = self.recognizer.recognize_google(audio).lower()
                    logger.info(f"Recognized command: {command}")
                    return command
                except sr.UnknownValueError:
                    self.speak("Sorry, I didn't catch that. Could you repeat?")
                except sr.RequestError as e:
                    logger.error(f"Could not request results from Google Speech Recognition service; {e}")
        
            except Exception as e:
                logger.error(f"Error in voice recognition: {e}")
                time.sleep(1)

    def speak(self, text):
        """Speak the given text while preventing multiple threads from interfering."""
        def _speak():
            with self.speak_lock:
                logger.info(f"Speaking: {text}")
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()

        threading.Thread(target=_speak, daemon=True).start()