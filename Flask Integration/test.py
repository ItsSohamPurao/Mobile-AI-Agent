from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return "Hello, Flask!"

@app.route('/api/test', methods=['GET'])
def test_api():
    return jsonify({"message": "API is working!"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)