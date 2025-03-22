from model import FirstLayerDMM  # Import decision-making model
from RealTime import RealtimeSearchEngine  # Import real-time search handler
from SpeechToText import SpeechRecognition  # Import speech recognition function
import requests  # For Flask API requests
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Get the spoken text
try:
    speech_text = SpeechRecognition()  # Recognized speech
    logging.info(f"Recognized speech: {speech_text}")
except Exception as e:
    logging.error(f"Speech recognition failed: {e}")
    speech_text = ""

if speech_text:
    Text = speech_text.split()[0]  # Extract the first word

    ollama_funcs = ["google search", "general", "realtime", "play", "youtube search"]

    FLASK_API_URL = "http://127.0.0.1:5000/execute"  # Flask API URL

    # Use FirstLayerDMM to classify the query
    try:
        query_type = FirstLayerDMM(speech_text)[0]  # Get classification result
        logging.info(f"Query type: {query_type}")
    except Exception as e:
        logging.error(f"Query classification failed: {e}")
        query_type = "general (query)"  # Fallback to general query

    if query_type.split()[0] in ollama_funcs:  # If it's an Ollama function
        try:
            answer = RealtimeSearchEngine(speech_text)  # Call the function correctly
            logging.info(f"Ollama Response: {answer}")
            print(f"Ollama Response: {answer}")
        except Exception as e:
            logging.error(f"Realtime search failed: {e}")
            answer = "Sorry, I couldn't process your request."
            print(answer)



    
