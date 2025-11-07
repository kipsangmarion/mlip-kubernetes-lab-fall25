from flask import Flask, request
import itertools
import requests

app = Flask(__name__)

# TODO: Add backend server URL for round-robin distribution
BACKEND_SERVERS = [
     "http://flask-backend-service:5001"
]

# Round-robin iterator for distributing requests
server_pool = itertools.cycle(BACKEND_SERVERS)

@app.route('/model-info')
def load_balance():
    backend_url = next(server_pool)
    response = requests.get(f"{backend_url}/model-info")
    try:
        data = response.json()
    except ValueError:
        return {"error": "Invalid JSON from backend", "raw": response.text}, 502
    return data, response.status_code

@app.route('/predict', methods=['POST'])
def predict():
    backend_url = next(server_pool)
    url = f"{backend_url}/predict"

    # TODO: Implement the rest of the POST request for the predict endpoint
    try:
        user_input = request.get_json(silent=True)
        if not user_input:
            return {"error": "invalid or missing JSON input"}, 400
        response = requests.post(url, json=user_input, timeout=10)
        data = response.json()
        return data, response.status_code
    except Exception as e:
        return {"error": f"Failed to reach backend: {e}"}, 502


if __name__ == '__main__':
    # TODO: Change the port if necessary (default is 8080)
    app.run(host='0.0.0.0', port=8080)
