# adb_commands.py
import subprocess
import os
import logging
import re
import time

logger = logging.getLogger(__name__)

class ADBCommands:
    def __init__(self, adb_path=None):
        self.adb_path = adb_path or self.find_adb_path()
        logger.info(f"Using ADB path: {self.adb_path}")

    def find_adb_path(self):
        """Locate ADB executable."""
        # (Same as the original find_adb_path method)
        ...

    def verify_device_connection(self):
        """Verify that at least one Android device is connected."""
        # (Same as the original verify_device_connection method)
        ...

    def take_screenshot(self):
        """Take a screenshot on the connected Android device."""
        # (Same as the original take_screenshot method)
        ...

    def adb_tap(self, x, y):
        """Simulate a tap at (x, y) coordinates using ADB."""
        # (Same as the original adb_tap method)
        ...

    def adb_key_event(self, key_code):
        """Send a key event using ADB."""
        # (Same as the original adb_key_event method)
        ...

    def adb_input_text(self, text):
        """Simulate text input using ADB."""
        # (Same as the original adb_input_text method)
        ...

    def open_app(self, app_package, app_name=None):
        """Open a specific Android app."""
        # (Same as the original open_app method)
        ...

    def navigate_home(self):
        """Navigate to the home screen."""
        # (Same as the original navigate_home method)
        ...

    def navigate_back(self):
        """Navigate back."""
        # (Same as the original navigate_back method)
        ...

    def adjust_volume(self, direction):
        """Adjust device volume."""
        # (Same as the original adjust_volume method)
        ...