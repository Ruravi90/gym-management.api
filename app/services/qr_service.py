import hmac
import hashlib
import time
import uuid
import json
from typing import Optional
from app.config import settings


QR_TOKEN_EXPIRY_SECONDS = 30
QR_NONCE_TTL_SECONDS = 120


def generate_qr_token(client_id: int) -> str:
    nonce = uuid.uuid4().hex
    ts = int(time.time())
    payload = {"cid": client_id, "ts": ts, "n": nonce}
    payload_b64 = _b64url_encode(json.dumps(payload, separators=(",", ":")).encode())
    sig = _sign(payload_b64)
    return f"{payload_b64}.{sig}"


def validate_qr_token(token: str) -> Optional[dict]:
    parts = token.split(".")
    if len(parts) != 2:
        return None
    payload_b64, sig = parts
    expected_sig = _sign(payload_b64)
    if not hmac.compare_digest(sig, expected_sig):
        return None
    try:
        payload = json.loads(_b64url_decode(payload_b64))
    except Exception:
        return None
    ts = payload.get("ts", 0)
    now = int(time.time())
    if abs(now - ts) > QR_TOKEN_EXPIRY_SECONDS:
        return None
    return payload


def get_qr_nonce(token: str) -> Optional[str]:
    parts = token.split(".")
    if len(parts) != 2:
        return None
    try:
        payload = json.loads(_b64url_decode(parts[0]))
        return payload.get("n")
    except Exception:
        return None


def _sign(payload_b64: str) -> str:
    key = settings.SECRET_KEY.encode()
    return hmac.new(key, payload_b64.encode(), hashlib.sha256).hexdigest()


def _b64url_encode(data: bytes) -> str:
    import base64
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def _b64url_decode(s: str) -> bytes:
    import base64
    s += "=" * (4 - len(s) % 4)
    return base64.urlsafe_b64decode(s)
