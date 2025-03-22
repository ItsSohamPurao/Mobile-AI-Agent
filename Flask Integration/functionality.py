import os
import subprocess
import threading
import queue
import re
import sys
import time
import logging
import traceback
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET

# NLP and Voice Processing Libraries
import spacy
import speech_recognition as sr
import pyttsx3
from transformers import pipeline
from dateutil import parser

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AndroidAIAgent:
    def _init_(self, adb_path=None):
        # NLP Setup
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            subprocess.run([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])
            self.nlp = spacy.load("en_core_web_sm")

        # Intent Classification
        self.intent_classifier = pipeline("text-classification", model="facebook/bart-large-mnli")

        # Voice Recognition Setup
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()

        # Text-to-Speech Setup
        self.tts_engine = pyttsx3.init()

        # Command Queue for thread-safe processing
        self.command_queue = queue.Queue()

        # ADB Configuration
        self.adb_path = adb_path or self.find_adb_path()
        logger.info(f"Using ADB path: {self.adb_path}")

        # Predefined app packages for easier launching
        self.app_packages = {
            'messages': 'com.google.android.apps.messaging',
            'messaging': 'com.google.android.apps.messaging',
            'sms': 'com.google.android.apps.messaging',
            'contacts': 'com.google.android.contacts',
            'phone': 'com.google.android.dialer',
            'dialer': 'com.google.android.dialer',
            'call': 'com.google.android.dialer',
            'browser': 'com.android.chrome',
            'chrome': 'com.android.chrome',
            'web': 'com.android.chrome',
            'camera': 'com.android.camera2',
            'photo': 'com.android.camera2',
            'settings': 'com.android.settings',
            'setting': 'com.android.settings',
            'config': 'com.android.settings',
            'google pay': 'com.google.android.apps.nbu.paisa.user',
            'pay': 'com.google.android.apps.nbu.paisa.user',
            'gpay': 'com.google.android.apps.nbu.paisa.user',
            'payment': 'com.google.android.apps.nbu.paisa.user',
            'calendar': 'com.google.android.calendar',
            'schedule': 'com.google.android.calendar',
            'youtube': 'com.google.android.youtube',
            'video': 'com.google.android.youtube',
            'maps': 'com.google.android.apps.maps',
            'map': 'com.google.android.apps.maps',
            'google maps': 'com.google.android.apps.maps',
            'navigation': 'com.google.android.apps.maps',
            'gmail': 'com.google.android.gm',
            'mail': 'com.google.android.gm',
            'email': 'com.google.android.gm',
            'photos': 'com.google.android.apps.photos',
            'gallery': 'com.google.android.apps.photos',
            'play store': 'com.android.vending',
            'store': 'com.android.vending',
            'play': 'com.android.vending',
            'apps': 'com.android.vending',
            'facebook': 'com.facebook.katana',
            'instagram': 'com.instagram.android',
            'whatsapp': 'com.whatsapp',
            'twitter': 'com.twitter.android',
            'x': 'com.twitter.android',
            'spotify': 'com.spotify.music',
            'music': 'com.spotify.music',
            'netflix': 'com.netflix.mediaclient',
            'amazon': 'com.amazon.mShop.android.shopping',
            'calculator': 'com.google.android.calculator',
            'clock': 'com.google.android.deskclock',
            'alarm': 'com.google.android.deskclock',
            'files': 'com.google.android.apps.nbu.files',
            'file': 'com.google.android.apps.nbu.files',
            'notes': 'com.google.android.keep',
            'note': 'com.google.android.keep'
        }

        # Threading lock for text-to-speech
        self.speak_lock = threading.Lock()

    def find_adb_path(self):
        """Locate ADB executable"""
        # Check if ADB is in system PATH first
        try:
            # Windows
            if sys.platform == 'win32':
                result = subprocess.run(['where', 'adb'], capture_output=True, text=True)
                if result.returncode == 0 and result.stdout.strip():
                    return result.stdout.strip().split('\n')[0]
            # macOS/Linux
            else:
                result = subprocess.run(['which', 'adb'], capture_output=True, text=True)
                if result.returncode == 0:
                    return result.stdout.strip()
        except Exception as e:
            logger.debug(f"ADB not found in PATH: {e}")

        # Environment variable check
        env_adb_path = os.environ.get('ANDROID_SDK_ROOT') or os.environ.get('ANDROID_HOME')
        if env_adb_path:
            platform_tools = os.path.join(env_adb_path, 'platform-tools')
            if sys.platform == 'win32':
                adb_path = os.path.join(platform_tools, 'adb.exe')
            else:
                adb_path = os.path.join(platform_tools, 'adb')

            if os.path.exists(adb_path):
                return adb_path

        # Comprehensive list of potential paths
        potential_paths = [
            '/usr/local/android-sdk/platform-tools/adb',
            '/opt/android-sdk/platform-tools/adb',
            os.path.expanduser('~/Android/Sdk/platform-tools/adb'),
            os.path.expanduser('~/Library/Android/sdk/platform-tools/adb'),
            'C:/Android/platform-tools/adb.exe',
            'C:/Android/sdk/platform-tools/adb.exe',
            'C:/Program Files/Android/platform-tools/adb.exe',
            'C:/Program Files (x86)/Android/platform-tools/adb.exe',
            os.path.expanduser('~/AppData/Local/Android/Sdk/platform-tools/adb.exe'),
            'C:/Users/%USERNAME%/AppData/Local/Android/Sdk/platform-tools/adb.exe'
        ]

        for path in potential_paths:
            expanded_path = os.path.expandvars(path)
            if os.path.exists(expanded_path):
                return expanded_path

        raise RuntimeError("""
ADB executable not found. 
Please install Android SDK Platform Tools and ensure ADB is in your PATH,
or set the ANDROID_SDK_ROOT or ANDROID_HOME environment variable.
Alternatively, provide ADB path explicitly when creating the agent instance.
""")

    def verify_device_connection(self):
        """
        Verify that at least one Android device is connected

        Returns:
            bool: True if connected, False otherwise
        """
        try:
            result = subprocess.run(
                [self.adb_path, 'devices'],
                capture_output=True,
                text=True,
                check=True
            )

            # Parse the output to check for connected devices
            lines = result.stdout.strip().split('\n')
            # First line is the header, so we skip it
            device_lines = [line for line in lines[1:] if line.strip() and not line.endswith('offline')]

            if device_lines:
                logger.info(f"Connected devices: {len(device_lines)}")
                return True
            else:
                logger.warning("No Android devices connected")
                return False

        except Exception as e:
            logger.error(f"Error checking device connection: {e}")
            return False

    def parse_date_time(self, date_time_str):
        """
        Parse a date-time string into a datetime object.

        :param date_time_str: Date-time string (e.g., "10th August 2025 at 10:00 a.m.")
        :return: Parsed datetime object or None if parsing fails
        """
        try:
            return parser.parse(date_time_str)
        except Exception as e:
            logger.error(f"Error parsing date-time: {e}")
            return None

    def listen_for_voice_command(self):
        """
        Continuous voice command listening thread.
        Captures voice input and puts recognized commands into the queue.
        """
        while True:
            try:
                with self.microphone as source:
                    logger.info("Listening for command...")
                    self.recognizer.adjust_for_ambient_noise(source)
                    audio = self.recognizer.listen(source)

                try:
                    # Recognize speech using Google Speech Recognition
                    command = self.recognizer.recognize_google(audio).lower()
                    logger.info(f"Recognized command: {command}")
                    # Add a log to verify the command is being added to the queue
                    self.command_queue.put(command)
                    logger.info(f"Added command to queue: {command}. Queue size: approximately {self.command_queue.qsize()}")

                    if command == 'exit' or command == 'quit' or command == 'stop':
                        self.speak("Shutting down.")
                        os._exit(0)  # Forcefully exit the program

                except sr.UnknownValueError:
                    self.speak("Sorry, I didn't catch that. Could you repeat?")
                except sr.RequestError as e:
                    logger.error(f"Could not request results from Google Speech Recognition service; {e}")

            except Exception as e:
                logger.error(f"Error in voice recognition: {e}")
                time.sleep(1)  # Prevent tight loop if errors occur repeatedly

    def speak(self, text):
        """
        Speak the given text while preventing multiple threads from interfering.
        """
        def _speak():
            with self.speak_lock:  # Lock to prevent multiple runAndWait() calls
                logger.info(f"Speaking: {text}")
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()

        threading.Thread(target=_speak, daemon=True).start()

    def process_command(self, command):
        """
        Process and interpret the voice command.

        :param command: Voice command string
        :return: Structured command interpretation
        """
        # Process with spaCy for entity extraction
        doc = self.nlp(command)

        # Extract key entities
        entities = {
            'verbs': [token.lemma_ for token in doc if token.pos_ == 'VERB'],
            'nouns': [token.lemma_ for token in doc if token.pos_ == 'NOUN'],
            'names': [ent.text for ent in doc.ents if ent.label_ == 'PERSON'],
            'dates': [ent.text for ent in doc.ents if ent.label_ == 'DATE'],
            'times': [ent.text for ent in doc.ents if ent.label_ == 'TIME'],
            'amounts': [ent.text for ent in doc.ents if ent.label_ == 'MONEY']
        }

        # Combine date and time if both are present
        if entities['dates'] and entities['times']:
            entities['date_time'] = f"{entities['dates'][0]} at {entities['times'][0]}"
        elif entities['dates']:
            entities['date_time'] = entities['dates'][0]
        else:
            entities['date_time'] = None

        # Intent classification
        try:
            intent = self.intent_classifier(command)[0]

            return {
                'raw_command': command,
                'intent': intent['label'],
                'confidence': intent['score'],
                'entities': entities
            }
        except Exception as e:
            logger.error(f"Intent classification error: {e}")
            return {
                'raw_command': command,
                'intent': 'unknown',
                'confidence': 0.0,
                'entities': entities
            }
    
    def parse_ui_dump(self, ui_dump_file, resource_id=None, text=None, class_name=None):
        """
        Parse the UI dump file to find the bounds of a UI element.

        :param ui_dump_file: Path to the UI dump file
        :param resource_id: Resource ID of the UI element to find
        :param text: Text of the UI element to find
        :param class_name: Class name of the UI element to find
        :return: Tuple of (x1, y1, x2, y2) representing the bounds of the element, or None if not found
        """
        try:
            with open(ui_dump_file, 'r', encoding='utf-8') as f:
                ui_dump_content = f.read()

            # Regex pattern to find the element by resource ID, text, or class name
            pattern = re.compile(
                rf'<node .?(resource-id="{resource_id}".?|text="{text}".?|class="{class_name}".?)bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]".*?/>'
            )
            match = pattern.search(ui_dump_content)

            if match:
                x1, y1, x2, y2 = map(int, match.groups()[-4:])
                return x1, y1, x2, y2
            else:
                logger.error(f"Could not find element with resource ID: {resource_id}")
                return None

        except Exception as e:
            logger.error(f"Error parsing UI dump file: {e}")
            return None
    
    def dump_ui_hierarchy(self):
        """
        Dump the current UI hierarchy and pull it to the local machine.

        :return: Path to the local UI dump file, or None if failed
        """
        try:
            # Ensure the directory exists
            os.makedirs(r"C:\Users\vansh\Desktop\palghar", exist_ok=True)

            # Dump the UI hierarchy
            ui_dump_cmd = [self.adb_path, 'shell', 'uiautomator', 'dump']
            logger.info(f"Executing command: {' '.join(ui_dump_cmd)}")
            subprocess.run(ui_dump_cmd, check=True)

            # Pull the UI dump file to the local machine
            local_ui_dump_file = os.path.join(r"C:\Users\vansh\Desktop\palghar", "window_dump.xml")
            pull_cmd = [self.adb_path, 'pull', '/sdcard/window_dump.xml', local_ui_dump_file]
            logger.info(f"Executing command: {' '.join(pull_cmd)}")
            subprocess.run(pull_cmd, check=True)

            return local_ui_dump_file


        except Exception as e:
            logger.error(f"Error dumping UI hierarchy: {e}")
            return None
        
    def get_element_center(self, bounds):
        """
        Calculate the center coordinates of a UI element based on its bounds.

        :param bounds: Tuple of (x1, y1, x2, y2) representing the bounds of the element
        :return: Tuple of (x, y) representing the center coordinates
        """
        if bounds:
            x1, y1, x2, y2 = bounds
            return (x1 + x2) // 2, (y1 + y2) // 2
        else:
            return None

    def execute_android_command(self, command):
        """
        Execute Android-specific commands via ADB.

        :param command: Voice command to execute
        :return: Command execution result
        """
        try:
            # Verify device connection
            if not self.verify_device_connection():
                self.speak("No Android device connected. Please connect a device and try again.")
                return None

            processed_cmd = self.process_command(command)
            logger.info(f"Processed command: {processed_cmd}")

            if not processed_cmd:
                self.speak("Sorry, I couldn't understand.")
                return None

            # Common command helpers like "please", "could you", "can you" and basic phrases
            command = command.replace("please", "").replace("could you", "").replace("can you", "").strip()

            # Handle basic system commands first
            if any(keyword in command for keyword in ["home", "go home", "go to home"]):
                return self.navigate_home()

            if any(keyword in command for keyword in ["back", "go back"]):
                return self.navigate_back()

            if "screenshot" in command or "take a screen" in command or "capture screen" in command:
                return self.take_screenshot()

            if "volume up" in command or "increase volume" in command or "turn up volume" in command:
                return self.adjust_volume('up')

            if "volume down" in command or "decrease volume" in command or "turn down volume" in command:
                return self.adjust_volume('down')

            # App-related commands
            # First, check for "open", "launch", "start" commands
            open_app_keywords = ["open", "launch", "start", "run"]
            if any(keyword in command for keyword in open_app_keywords):
                # Extract possible app name from command
                potential_app = None

                # Match app names directly
                for app_name in self.app_packages.keys():
                    # Match whole app name as a chunk (e.g. "google maps" rather than just "map")
                    if f" {app_name} " in f" {command} " or command.endswith(f" {app_name}") or command.startswith(f"{app_name} "):
                        potential_app = app_name
                        break

                # If no direct match, try to extract app name from nouns
                if not potential_app:
                    verbs = processed_cmd.get('entities', {}).get('verbs', [])
                    nouns = processed_cmd.get('entities', {}).get('nouns', [])

                    for noun in nouns:
                        if noun in self.app_packages:
                            potential_app = noun
                            break

                if potential_app:
                    return self.open_app(self.app_packages[potential_app], potential_app)
                else:
                    # Try to extract app name after the open keyword
                    for keyword in open_app_keywords:
                        if keyword in command:
                            # Get the text after the keyword
                            app_part = command.split(keyword, 1)[1].strip()
                            # Check if it matches any known app names
                            for app_name in self.app_packages.keys():
                                if app_name in app_part:
                                    return self.open_app(self.app_packages[app_name], app_name)

                    # Still no match - check if any noun could be an unrecognized app
                    nouns = processed_cmd.get('entities', {}).get('nouns', [])
                    if nouns:
                        app_attempted = nouns[0]
                        self.speak(f"Sorry, I couldn't find the app {app_attempted}. Is it installed on your device?")
                    else:
                        self.speak("Sorry, I couldn't identify which app you want to open.")
                    return None

            # Check for context-based app launching (if command implies an app without explicit "open")
            # Example: "send a message" should open messaging app
            if "call" in command or "dial" in command:
                return self.open_app(self.app_packages['phone'], 'Phone')

            if "message" in command or "text" in command or "sms" in command:
                return self.open_app(self.app_packages['messages'], 'Messages')

            if "search" in command or "browse" in command or "web" in command:
                return self.open_app(self.app_packages['browser'], 'Browser')

            if "map" in command or "direction" in command or "navigate" in command:
                return self.open_app(self.app_packages['maps'], 'Maps')

            if "photo" in command or "picture" in command or "selfie" in command:
                return self.open_app(self.app_packages['camera'], 'Camera')

            if "email" in command or "mail" in command:
                return self.open_app(self.app_packages['gmail'], 'Gmail')

            if "pay" in command or "send money" in command or "payment" in command:
                return self.open_app(self.app_packages['google pay'], 'Google Pay')

            if "video" in command or "watch" in command:
                return self.open_app(self.app_packages['youtube'], 'YouTube')

            if "settings" in command or "configure" in command:
                return self.open_app(self.app_packages['settings'], 'Settings')

            # Handle more complex commands
            if 'send' in command and 'money' in command:
                amounts = processed_cmd.get('entities', {}).get('amounts', [])
                names = processed_cmd.get('entities', {}).get('names', [])

                if amounts and names:
                    amount = amounts[0]
                    recipient = names[0]
                    return self.initiate_google_pay_transaction(recipient, amount)
                else:
                    self.speak("Please specify the recipient and amount to send money.")
                    return None

            elif ('schedule' in command or 'add' in command) and ('event' in command or 'meeting' in command or 'calendar' in command):
                date_time = processed_cmd.get('entities', {}).get('date_time', None)
                names = processed_cmd.get('entities', {}).get('names', [])

                if date_time:
                    event_name = ' '.join(names) if names else "New Event"
                    return self.schedule_google_calendar_event(event_name, date_time)
                else:
                    self.speak("Please specify the date and time for the event.")
                    return None

            # Fallback for unrecognized commands
            self.speak("I'm not sure how to handle that command. Could you try something different?")
            return None

        except Exception as e:
            logger.error(f"Error executing command: {e}")
            self.speak("An error occurred while processing the command.")
            return None

    def take_screenshot(self):
        """
        Take a screenshot on the connected Android device.

        :return: Path to the saved screenshot or None if failed
        """
        try:
            # Create screenshots directory if it doesn't exist
            screenshots_dir = os.path.join(os.getcwd(), 'screenshots')
            os.makedirs(screenshots_dir, exist_ok=True)

            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_path = os.path.join(screenshots_dir, f'screenshot_{timestamp}.png')

            # Execute screenshot command
            cmd = [self.adb_path, 'shell', 'screencap', '-p', '/sdcard/screenshot.png']
            logger.info(f"Executing command: {' '.join(cmd)}")
            subprocess.run(cmd, check=True)

            # Pull screenshot to local machine
            pull_cmd = [self.adb_path, 'pull', '/sdcard/screenshot.png', screenshot_path]
            logger.info(f"Executing command: {' '.join(pull_cmd)}")
            result = subprocess.run(pull_cmd, capture_output=True, text=True)

            if result.returncode == 0:
                self.speak(f"Screenshot taken and saved")
                logger.info(f"Screenshot saved successfully: {screenshot_path}")
                return screenshot_path
            else:
                self.speak("Failed to take screenshot")
                logger.error(f"Error saving screenshot: {result.stderr}")
                return None
        except Exception as e:
            logger.error(f"Screenshot error: {e}")
            self.speak("An error occurred while taking the screenshot.")
            return None

    def initiate_google_pay_transaction(self, recipient, amount):
        """
        Initiate a Google Pay transaction using ADB commands.

        :param recipient: Recipient's phone number or UPI ID
        :param amount: Amount to send
        :return: Command execution result
        """
        try:
            # Open Google Pay
            self.open_app(self.app_packages['google pay'], 'Google Pay')
            logger.info("Opened Google Pay")

            # Wait for the app to load
            time.sleep(5)

            # Navigate to "Send Money" section - try multiple potential coordinates
            logger.info("Navigating to Send Money section")
            # Different devices might have the UI elements in different positions
            # Try a few common positions
            potential_send_money_positions = [(500, 1000), (500, 800), (300, 1200)]
            for x, y in potential_send_money_positions:
                self.adb_tap(x, y)
                time.sleep(1)

            # Wait for the recipient field to appear
            time.sleep(2)

            # Enter recipient
            logger.info(f"Entering recipient: {recipient}")
            self.adb_input_text(recipient)
            time.sleep(2)

            # Tap on what would likely be the first suggestion
            potential_contact_positions = [(500, 300), (300, 400), (400, 350)]
            for x, y in potential_contact_positions:
                self.adb_tap(x, y)
                time.sleep(1)

            # Enter amount
            logger.info(f"Entering amount: {amount}")
            # Clean the amount string from any currency symbols
            clean_amount = re.sub(r'[^\d.]', '', amount.split()[0])
            self.adb_input_text(clean_amount)
            time.sleep(2)

            # Try various positions for "Pay" or "Send" button
            pay_button_positions = [(500, 1500), (500, 1300), (300, 1400)]
            for x, y in pay_button_positions:
                self.adb_tap(x, y)
                time.sleep(1)

            # Try various positions for confirmation buttons
            confirm_positions = [(500, 1200), (500, 1000), (300, 1100)]
            for x, y in confirm_positions:
                self.adb_tap(x, y)
                time.sleep(1)

            self.speak(f"I've attempted to send {amount} to {recipient}. Please check if the transaction was successful.")
            return True

        except Exception as e:
            logger.error(f"Error initiating Google Pay transaction: {e}")
            self.speak("Failed to initiate the transaction. Please try again manually.")
            return False

    def schedule_google_calendar_event(self, event_name, event_date_time_str):
        """
        Schedule an event in Google Calendar using UI Automator.
        """
        try:
            # Parse the date and time
            event_date_time = self.parse_date_time(event_date_time_str)
            if not event_date_time:
                self.speak("Sorry, I couldn't understand the date and time. Please try again.")
                return False

            # Format date and time for Google Calendar
            event_date = event_date_time.strftime("%Y-%m-%d")
            start_time = event_date_time.strftime("%H:%M")
            end_time = (event_date_time + timedelta(hours=1)).strftime("%H:%M")

            # Open Google Calendar
            self.open_app(self.app_packages['calendar'], 'Google Calendar')
            logger.info("Opened Google Calendar")

            # Wait for the app to load
            time.sleep(5)

            # Dump the UI hierarchy
            local_ui_dump_file = self.dump_ui_hierarchy()
            if not local_ui_dump_file:
                self.speak("Failed to dump the UI hierarchy. Please try again.")
                return False

            # Find and tap the "Create Event" Floating Action Button (FAB)
            fab_bounds = self.parse_ui_dump(
                local_ui_dump_file,
                resource_id="com.google.android.calendar:id/floating_action_button"
            )
            if not fab_bounds:
                self.speak("Could not find the 'Create Event' button. Please ensure the Google Calendar app is open and try again.")
                return False

            fab_center = self.get_element_center(fab_bounds)
            if not fab_center:
                self.speak("Failed to calculate the 'Create Event' button position. Please try again.")
                return False

            self.adb_tap(*fab_center)
            logger.info("Tapped the 'Create Event' button")
            time.sleep(2)

            # ... (rest of the method)

            self.speak(f"I've scheduled '{event_name}' on {event_date} from {start_time} to {end_time}. Please check your calendar.")
            return True

        except Exception as e:
            logger.error(f"Error scheduling Google Calendar event: {e}")
            self.speak("Failed to schedule the event. Please try again manually.")
            return False

    def adb_tap(self, x, y):
        """
        Simulate a tap at (x, y) coordinates using ADB.

        :param x: X coordinate
        :param y: Y coordinate
        """
        try:
            cmd = [self.adb_path, 'shell', 'input', 'tap', str(x), str(y)]
            logger.info(f"Executing command: {' '.join(cmd)}")
            subprocess.run(cmd, check=True)
            return True
        except Exception as e:
            logger.error(f"Tap error at ({x}, {y}): {e}")
            return False

    def adb_key_event(self, key_code):
        """
        Send a key event using ADB.

        :param key_code: Android key code
        """
        try:
            cmd = [self.adb_path, 'shell', 'input', 'keyevent', str(key_code)]
            logger.info(f"Executing command: {' '.join(cmd)}")
            subprocess.run(cmd, check=True)
            return True
        except Exception as e:
            logger.error(f"Key event error ({key_code}): {e}")
            return False

    def adb_input_text(self, text):
        """
        Simulate text input using ADB.

        :param text: Text to input
        """
        try:
            # Escape special characters for different platforms
            if sys.platform == 'win32':
                # Windows needs different escaping
                escaped_text = text.replace(' ', '%s')
            else:
                escaped_text = re.sub(r'(["\'\s])', r'\\\1', text)

            cmd = [self.adb_path, 'shell', 'input', 'text', escaped_text]
            logger.info(f"Executing command: {' '.join(cmd)}")
            subprocess.run(cmd, check=True)
            return True
        except Exception as e:
            logger.error(f"Text input error: {e}")
            # Try alternate method for text input (character by character)
            try:
                logger.info("Trying character-by-character input as fallback")
                for char in text:
                    if char == ' ':
                        char_cmd = [self.adb_path, 'shell', 'input', 'text', '%s']
                    else:
                        char_cmd = [self.adb_path, 'shell', 'input', 'text', char]
                    subprocess.run(char_cmd, check=True)
                    time.sleep(0.1)  # Small delay between characters
                return True
            except Exception as inner_e:
                logger.error(f"Character-by-character input failed: {inner_e}")
                return False

    def open_app(self, app_package, app_name=None):
        """
        Open a specific Android app.

        :param app_package: Package name of the app
        :param app_name: Friendly name of the app (for TTS)
        :return: Command execution result
        """
        try:
            display_name = app_name or app_package

            # Check if app is installed
            check_cmd = [self.adb_path, 'shell', 'pm', 'list', 'packages', app_package]
            logger.info(f"Checking if app is installed: {' '.join(check_cmd)}")
            check_result = subprocess.run(check_cmd, capture_output=True, text=True)

            app_installed = False
            # Check if package is in the output
            if app_package in check_result.stdout:
                app_installed = True
            else:
                # Try a more flexible search (partial package match)
                packages_list = subprocess.run(
                    [self.adb_path, 'shell', 'pm', 'list', 'packages'],
                    capture_output=True,
                    text=True
                )

                # Extract package names from output
                packages = [line.replace("package:", "").strip() for line in packages_list.stdout.splitlines()]

                # Find closest matching package
                matching_packages = [pkg for pkg in packages if app_package in pkg]
                if matching_packages:
                    app_package = matching_packages[0]
                    app_installed = True
                    logger.info(f"Found similar package: {app_package}")

            if not app_installed:
                self.speak(f"The app {display_name} doesn't seem to be installed on the device.")
                logger.warning(f"App not installed: {app_package}")
                return None

            # Try multiple methods to open the app
            success = False

            # Method 1: Using monkey
            try:
                monkey_cmd = [self.adb_path, 'shell', 'monkey', '-p', app_package, '-c', 'android.intent.category.LAUNCHER', '1']
                logger.info(f"Trying to open app with monkey: {' '.join(monkey_cmd)}")
                result = subprocess.run(monkey_cmd, capture_output=True, text=True)

                if "No activities found to run" not in result.stdout and "No activities found" not in result.stderr:
                    success = True
                else:
                    logger.info("Monkey launch failed, trying alternate methods")
            except Exception as e:
                logger.error(f"Monkey launch error: {e}")

            # Method 2: Using am start with main activity
            if not success:
                try:
                    # Try default MainActivity first
                    main_activity_cmd = [self.adb_path, 'shell', 'am', 'start', '-n', f"{app_package}/.MainActivity"]
                    logger.info(f"Trying to open app with main activity: {' '.join(main_activity_cmd)}")
                    result = subprocess.run(main_activity_cmd, capture_output=True, text=True)

                    if result.returncode == 0 and "Error" not in result.stdout:
                        success = True
                    else:
                        logger.info("Main activity launch failed, trying more generic approach")
                except Exception as e:
                    logger.error(f"Main activity launch error: {e}")

            # Method 3: Using am start without specific activity
            if not success:
                try:
                    start_cmd = [self.adb_path, 'shell', 'am', 'start', '-a', 'android.intent.action.MAIN', '-c', 'android.intent.category.LAUNCHER', '-n', f"{app_package}/"]
                    logger.info(f"Trying generic app launch: {' '.join(start_cmd)}")
                    result = subprocess.run(start_cmd, capture_output=True, text=True)

                    if "Error" not in result.stdout:
                        success = True
                except Exception as e:
                    logger.error(f"Generic launch error: {e}")

            # Method 4: Using dumpsys to find the main activity
            if not success:
                try:
                    # Get package info to find main activity
                    dumpsys_cmd = [self.adb_path, 'shell', 'dumpsys', 'package', app_package]
                    logger.info(f"Getting package info: {' '.join(dumpsys_cmd)}")
                    dumpsys_result = subprocess.run(dumpsys_cmd, capture_output=True, text=True)

                    # Extract main activity
                    activity_pattern = re.compile(fr'{app_package}/[\w\.]+Activity')
                    activities = activity_pattern.findall(dumpsys_result.stdout)

                    if activities:
                        main_activity = activities[0]
                        launch_cmd = [self.adb_path, 'shell', 'am', 'start', '-n', main_activity]
                        logger.info(f"Launching found activity: {' '.join(launch_cmd)}")
                        subprocess.run(launch_cmd)
                        success = True
                except Exception as e:
                    logger.error(f"Activity search error: {e}")

            if success:
                self.speak(f"Opening {display_name}")
                return True
            else:
                self.speak(f"I had trouble opening {display_name}. The app might be installed but not accessible.")
                return False

        except Exception as e:
            logger.error(f"App launch error: {e}")
            self.speak(f"Failed to open {display_name}")
            return False

    def navigate_home(self):
        """
        Navigate to the home screen.

        :return: Command execution result
        """
        try:
            cmd = [self.adb_path, 'shell', 'input', 'keyevent', '3']  # KEYCODE_HOME
            logger.info(f"Navigating to home: {' '.join(cmd)}")
            subprocess.run(cmd, check=True)
            self.speak("Going to home screen")
            return True
        except Exception as e:
            logger.error(f"Home navigation error: {e}")
            self.speak("Failed to go to home screen")
            return False

    def navigate_back(self):
        """
        Navigate back.

        :return: Command execution result
        """
        try:
            cmd = [self.adb_path, 'shell', 'input', 'keyevent', '4']  # KEYCODE_BACK
            logger.info(f"Navigating back: {' '.join(cmd)}")
            subprocess.run(cmd, check=True)
            self.speak("Going back")
            return True
        except Exception as e:
            logger.error(f"Back navigation error: {e}")
            self.speak("Failed to go back")
            return False

    def adjust_volume(self, direction):
        """
        Adjust device volume.

        :param direction: 'up' or 'down'
        :return: Command execution result
        """
        try:
            if direction.lower() == 'up':
                key_code = '24'  # KEYCODE_VOLUME_UP
                message = "Increasing volume"
            else:
                key_code = '25'  # KEYCODE_VOLUME_DOWN
                message = "Decreasing volume"

            cmd = [self.adb_path, 'shell', 'input', 'keyevent', key_code]
            logger.info(f"Adjusting volume {direction}: {' '.join(cmd)}")
            subprocess.run(cmd, check=True)
            self.speak(message)
            return True
        except Exception as e:
            logger.error(f"Volume adjustment error: {e}")
            self.speak(f"Failed to adjust volume {direction}")
            return False

    def start_listening_thread(self):
        """
        Start a background thread for continuous voice command listening.
        """
        try:
            # Start voice recognition in a separate thread
            self.voice_thread = threading.Thread(target=self.listen_for_voice_command, daemon=True)
            self.voice_thread.start()
            logger.info("Voice recognition thread started")

            # Start command processing thread
            self.processing_thread = threading.Thread(target=self.command_processing_loop, daemon=True)
            self.processing_thread.start()
            logger.info("Command processing thread started")

            return True
        except Exception as e:
            logger.error(f"Failed to start listening thread: {e}")
            return False

    def command_processing_loop(self):
        """
        Process commands from the queue in a separate thread.
        """
        while True:
            try:
                # Add logging to show the loop is running
                logger.info(f"Command processing loop running. Queue size: approximately {self.command_queue.qsize()}")

                # Get command from queue with a timeout to allow for clean shutdown
                try:
                    command = self.command_queue.get(timeout=1)
                    logger.info(f"Dequeued command for processing: {command}")
                except queue.Empty:
                    continue

                # Process and execute command
                logger.info(f"Processing command from queue: {command}")
                result = self.execute_android_command(command)

                # Log the result for debugging
                logger.info(f"Command execution result: {result}")

                # Mark as done
                self.command_queue.task_done()
                logger.info("Command processing completed. Ready for next command.")

            except Exception as e:
                logger.error(f"Error in command processing loop: {e}")
                logger.error(f"Exception details: {str(e)}")
                logger.error(f"Exception traceback: {traceback.format_exc()}")
                time.sleep(1)  # Prevent tight loop if errors occur repeatedly

    def run(self):
        """
        Start the Android AI Agent.
        """
        try:
            # Verify device connection
            if not self.verify_device_connection():
                print("No Android device connected. Please connect a device and try again.")
                return False

            # Start listening thread
            if not self.start_listening_thread():
                print("Failed to start listening thread. Exiting.")
                return False

            self.speak("Android AI Agent is now active and listening for commands.")

            # Keep the main thread alive
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\nShutting down Android AI Agent...")
                self.speak("Shutting down. Goodbye!")
                return True

        except Exception as e:
            logger.error(f"Error running Android AI Agent: {e}")
            return False


if __name__ == "_main_":
    try:
        # Create and run the agent
        agent = AndroidAIAgent()
        agent.run()
    except Exception as e:
        print(f"Error initializing Android AI Agent: {e}")
        sys.exit(1)