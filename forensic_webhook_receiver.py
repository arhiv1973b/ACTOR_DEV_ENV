# forensic_webhook_receiver.py
import hmac
import hashlib
from flask import Flask, request, jsonify

app = Flask(__name__)

SECRET_KEY = b"supersecretkey"
EXPECTED_BEARER = "secure-token-123"


@app.route("/webhook/forensic", methods=["POST"])
def receive_forensic_report():
    # 1. Verify Bearer token authorization
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return jsonify({"error": "Unauthorized: Missing or invalid Bearer token"}), 401

    token = auth_header.split(" ")[1]
    if not hmac.compare_digest(token, EXPECTED_BEARER):
        return jsonify({"error": "Forbidden: Invalid token"}), 403

    # 2. Extract payload and signature
    data = request.get_json()
    if not data or "report" not in data or "signature" not in data:
        return jsonify({"error": "Bad Request: Missing report or signature"}), 400

    report_str = data["report"]
    received_signature = data["signature"]

    # 3. Compute expected HMAC-SHA256 signature
    computed_signature = hmac.new(
        SECRET_KEY, report_str.encode("utf-8"), hashlib.sha256
    ).hexdigest()

    # 4. Constant-time comparison to prevent timing attacks
    if not hmac.compare_digest(computed_signature, received_signature):
        return jsonify({"error": "Verification Failed: Invalid HMAC signature"}), 400

    # 5. Success - Signature verified, process report
    print("[SUCCESS] Forensic report received and signature verified successfully.")
    return jsonify(
        {
            "status": "VERIFIED_AND_ACCEPTED",
            "message": "HMAC signature verified successfully.",
        }
    ), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
