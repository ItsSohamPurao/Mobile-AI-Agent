from flask import Flask, request, jsonify, send_from_directory
from model import FirstLayerDMM
from RealTime import RealtimeSearchEngine
import os

app = Flask(__name__)

# Serve the Voice.html file
@app.route("/")
def serve_html():
    return send_from_directory(os.getcwd(), "Voice.html")

# Endpoint to process the recognized speech
@app.route("/process_query", methods=["POST"])
def process_query():
    data = request.json
    query = data.get("query", "")

    # Use FirstLayerDMM to classify the query
    query_type = FirstLayerDMM(query)[0]

    # List of functions handled by Realtime.py
    ollama_funcs = ["google search", "general", "realtime", "play", "youtube search"]

    # Check if the query type is handled by Realtime.py
    if query_type.split()[0] in ollama_funcs:
        # Call RealtimeSearchEngine to get the answer
        answer = RealtimeSearchEngine(query)
    else:
        answer = "This query type is not handled by Realtime.py."

    # Return the answer as a JSON response
    return jsonify({"answer": answer})

if __name__ == "__main__":
    app.run(debug=True)