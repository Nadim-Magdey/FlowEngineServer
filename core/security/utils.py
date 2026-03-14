import hmac
import hashlib
import time

SECRET = "1d56sa1d5a6s1d65as1d65as1a56dadas65d1d8a6s78vc97v8978a9sda"

def verify_request(request):
    try:
        token = request.headers.get("Authorization", "").replace("Token ", "")
        timestamp = request.headers.get("X-Timestamp")
        nonce = request.headers.get("X-Nonce")
        signature = request.headers.get("X-Signature")

        if not token or not timestamp or not nonce or not signature:
            return False

        body = request.body.decode()

        message = f"{token}{timestamp}{nonce}{body}"

        expected = hmac.new(
            SECRET.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()

        if not hmac.compare_digest(signature, expected):
            return False

        if abs(time.time() - int(timestamp)) > 30:
            return False

        return True

    except Exception:
        return False
