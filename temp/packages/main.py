# main.py
import logging
from voice_processing import VoiceProcessor
from nlp_processing import NLPProcessor
from adb_commands import ADBCommands
from command_processing import CommandProcessor
import threading
import time
import sys

logger = logging.getLogger(__name__)

class AndroidAIAgent:
    def __init__(self):
        self.voice_processor = VoiceProcessor()
        self.nlp_processor = NLPProcessor()
        self.adb_commands = ADBCommands()
        self.command_processor = CommandProcessor(self.adb_commands, self.nlp_processor, self.voice_processor)

    def start_listening_thread(self):
        """Start a background thread for continuous voice command listening."""
        try:
            self.voice_thread = threading.Thread(target=self.voice_processor.listen_for_voice_command, daemon=True)
            self.voice_thread.start()
            logger.info("Voice recognition thread started")
            
            self.processing_thread = threading.Thread(target=self.command_processor.command_processing_loop, daemon=True)
            self.processing_thread.start()
            logger.info("Command processing thread started")
            return True
        except Exception as e:
            logger.error(f"Failed to start listening thread: {e}")
            return False

    def run(self):
        """Start the Android AI Agent."""
        try:
            if not self.adb_commands.verify_device_connection():
                print("No Android device connected. Please connect a device and try again.")
                return False
                
            if not self.start_listening_thread():
                print("Failed to start listening thread. Exiting.")
                return False
                
            self.voice_processor.speak("Android AI Agent is now active and listening for commands.")
            
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\nShutting down Android AI Agent...")
                self.voice_processor.speak("Shutting down. Goodbye!")
                return True
                
        except Exception as e:
            logger.error(f"Error running Android AI Agent: {e}")
            return False

if __name__ == "__main__":
    try:
        agent = AndroidAIAgent()
        agent.run()
    except Exception as e:
        print(f"Error initializing Android AI Agent: {e}")
        sys.exit(1)