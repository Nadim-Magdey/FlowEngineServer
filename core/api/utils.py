import time
import hmac
import hashlib
import secrets

SECRET = b"super_secret"  # server-side secret


def generate_token():
    """Generate a short-lived HMAC token"""
    nonce = secrets.token_hex(8)  # 16 chars
    ts = str(int(time.time()))
    data = f"{nonce}.{ts}"
    sig = hmac.new(SECRET, data.encode(), hashlib.sha256).hexdigest()
    token = f"{nonce}.{ts}.{sig}"
    print(f"[DEBUG] Generated token: {token}")
    return token

def verify_token(token, max_age=60):
    """Verify token signature and expiry with debug prints"""
    try:
        print(f"[DEBUG] Verifying token: {token}")
        parts = token.split(".")
        if len(parts) != 3:
            print("[DEBUG] Token format invalid")
            return None

        nonce, ts_str, sig = parts
        print(f"[DEBUG] nonce={nonce}, ts={ts_str}, sig={sig}")

        data = f"{nonce}.{ts_str}"
        expected_sig = hmac.new(SECRET, data.encode(), hashlib.sha256).hexdigest()
        print(f"[DEBUG] expected_sig={expected_sig}")

        # Check signature
        if not hmac.compare_digest(sig, expected_sig):
            print("[DEBUG] Signature mismatch")
            return None

        # Check expiry
        ts_int = int(ts_str)
        now = int(time.time())
        age = now - ts_int
        print(f"[DEBUG] Token timestamp={ts_int}, now={now}, age={age}s, max_age={max_age}s")
        if age > max_age:
            print("[DEBUG] Token expired")
            return None

        print("[DEBUG] Token valid")
        return nonce
    except Exception as e:
        print(f"[DEBUG] Exception in verify_token: {e}")
        return None
