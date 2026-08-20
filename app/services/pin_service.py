import time
import secrets
from typing import Optional


PIN_EXPIRY_SECONDS = 60
PIN_LENGTH = 6


_pins: dict[str, dict] = {}


def generate_pin(client_id: int) -> str:
    ts = int(time.time())
    pin = _random_pin()
    _pins[pin] = {"cid": client_id, "ts": ts}
    _cleanup_expired()
    return pin


def validate_pin(pin: str) -> Optional[dict]:
    if len(pin) != PIN_LENGTH or not pin.isdigit():
        return None
    payload = _pins.get(pin)
    if payload is None:
        return None
    ts = payload.get("ts", 0)
    now = int(time.time())
    if abs(now - ts) > PIN_EXPIRY_SECONDS:
        _pins.pop(pin, None)
        return None
    _pins.pop(pin, None)
    return payload


def _random_pin() -> str:
    while True:
        pin = "".join(secrets.choice("0123456789") for _ in range(PIN_LENGTH))
        if pin not in _pins:
            return pin


def _cleanup_expired():
    now = int(time.time())
    expired = [p for p, data in _pins.items() if abs(now - data["ts"]) > PIN_EXPIRY_SECONDS * 2]
    for p in expired:
        _pins.pop(p, None)
