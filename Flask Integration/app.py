from flask import Flask, request, jsonify, render_template
from extra import AndroidAIAgent  # Import the AndroidAIAgent class from main.py

app = Flask(__name__)

# Initialize the AndroidAIAgent
agent = AndroidAIAgent()

@app.route('/')
def index():
    """ Serve the HTML page """
    return render_template("index.html")

@app.route('/api/process_voice', methods=['POST'])
def process_voice():
    """
    Endpoint to process voice commands sent from the website.
    """
    try:
        data = request.get_json()
        command = data.get('command')

        if not command:
            return jsonify({"error": "No command provided"}), 400

        # Send the command to AndroidAIAgent
        result = agent.execute_android_command(command)

        if result is None:
            return jsonify({"error": "Failed to process command"}), 500
        
        return jsonify({"result": result}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)


@app.route('/api/status', methods=['GET','POST'])
def status():
    """
    Endpoint to check the status of the AndroidAIAgent.
    """
    try:
        # Check if the agent is running
        return jsonify({"status": "running"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)