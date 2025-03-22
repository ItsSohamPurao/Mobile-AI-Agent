import speech_recognition as sr
import requests
import json

# Flask API URL (Update this if Flask is running on a different machine)
FLASK_API_URL = "http://127.0.0.1:5000/api/process_command"

def recognize_speech():
    """Capture voice input and convert it into text."""
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        print("Listening... Speak your command now.")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        # Convert speech to text using Google Speech Recognition
        command = recognizer.recognize_google(audio)
        print(f"Recognized Command: {command}")
        return command
    except sr.UnknownValueError:
        print("Sorry, could not understand the audio.")
        return None
    except sr.RequestError:
        print("Could not request results from the speech recognition service.")
        return None

def send_command_to_flask(command):
    """Send the recognized command to the Flask API."""
    if not command:
        print("No valid command to send.")
        return
    
    payload = {"command": command}
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(FLASK_API_URL, json=payload, headers=headers)
        data = response.json()
        print(f"Response from Flask API: {data}")
    except requests.exceptions.RequestException as e:
        print(f"Error communicating with Flask API: {e}")

if __name__ == "__main__":
    while True:
        print("\nPress Enter to start speaking or type 'exit' to quit.")
        user_input = input()
        if user_input.lower() == "exit":
            break

        command = recognize_speech()
        send_command_to_flask(command)
