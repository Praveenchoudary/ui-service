from flask import Flask, render_template, request, jsonify
import requests
import os

app = Flask(__name__)

BOOKING_SERVICE_URL = os.environ.get("BOOKING_SERVICE_URL", "http://localhost:8082")

@app.route("/health")
def health():
    return jsonify({"status": "healthy", "service": "ui-service"}), 200

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/api/book", methods=["POST"])
def book():
    data = request.get_json()
    try:
        response = requests.post(
            f"{BOOKING_SERVICE_URL}/book",
            json=data,
            timeout=8
        )
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"status": "failed", "reason": f"booking-service unreachable: {str(e)}"}), 503

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
