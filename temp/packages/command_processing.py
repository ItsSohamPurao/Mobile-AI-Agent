# command_processing.py
import queue
import logging
import time

logger = logging.getLogger(__name__)

class CommandProcessor:
    def __init__(self, adb_commands, nlp_processor, voice_processor):
        self.adb_commands = adb_commands
        self.nlp_processor = nlp_processor
        self.voice_processor = voice_processor
        self.command_queue = queue.Queue()

    def execute_android_command(self, command):
        """Execute Android-specific commands via ADB."""
        # (Same as the original execute_android_command method)
        ...

    def command_processing_loop(self):
        """Process commands from the queue in a separate thread."""
        while True:
            try:
                logger.info(f"Command processing loop running. Queue size: approximately {self.command_queue.qsize()}")
                try:
                    command = self.command_queue.get(timeout=1)
                    logger.info(f"Dequeued command for processing: {command}")
                except queue.Empty:
                    continue

                result = self.execute_android_command(command)
                logger.info(f"Command execution result: {result}")
                self.command_queue.task_done()
                logger.info("Command processing completed. Ready for next command.")
            
            except Exception as e:
                logger.error(f"Error in command processing loop: {e}")
                time.sleep(1)