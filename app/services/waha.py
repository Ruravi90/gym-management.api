import logging
from typing import Optional

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


def tenant_session_name(tenant_id: int) -> str:
    return f"tenant-{tenant_id}"


async def _waha_request(method: str, path: str, **kwargs) -> httpx.Response:
    if not settings.WAHA_ENABLED or not settings.WAHA_BASE_URL:
        raise RuntimeError("WAHA está deshabilitado o no tiene URL configurada")
    api_key = settings.WAHA_API_KEY_PLAIN or settings.WAHA_API_KEY
    if api_key.startswith("sha512:"):
        api_key = ""
    headers = {"X-Api-Key": api_key} if api_key else {}
    async with httpx.AsyncClient(timeout=settings.WAHA_TIMEOUT_SECONDS) as client:
        return await client.request(method, f"{settings.WAHA_BASE_URL.rstrip('/')}{path}", headers=headers, **kwargs)


async def create_or_start_tenant_session(tenant_id: int) -> dict:
    session = tenant_session_name(tenant_id)
    response = await _waha_request("POST", "/api/sessions", json={"name": session})
    if response.status_code not in (200, 201, 409):
        response.raise_for_status()
    status_response = await _waha_request("GET", f"/api/sessions/{session}")
    if status_response.status_code == 404:
        start_response = await _waha_request("POST", f"/api/sessions/{session}/start")
        if start_response.status_code not in (200, 201, 202, 409):
            start_response.raise_for_status()
        status_response = await _waha_request("GET", f"/api/sessions/{session}")
    status_response.raise_for_status()
    return {"session": session, **status_response.json()}


async def get_tenant_session_status(tenant_id: int) -> dict:
    return await get_session_status(tenant_session_name(tenant_id))


async def get_session_status(session: str) -> dict:
    response = await _waha_request("GET", f"/api/sessions/{session}")
    if response.status_code == 404:
        return {"session": session, "status": "NOT_FOUND", "active": False}
    response.raise_for_status()
    data = response.json()
    return {"session": session, **data, "active": data.get("status") == "WORKING"}


async def get_tenant_qr(tenant_id: int) -> httpx.Response:
    return await get_session_qr(tenant_session_name(tenant_id))


async def get_session_qr(session: str) -> httpx.Response:
    return await _waha_request("GET", f"/api/{session}/auth/qr")


async def logout_tenant_session(tenant_id: int) -> dict:
    return await logout_session(tenant_session_name(tenant_id))


async def logout_session(session: str) -> dict:
    response = await _waha_request("POST", f"/api/sessions/{session}/logout")
    if response.status_code == 404:
        return {"session": session, "status": "NOT_FOUND"}
    response.raise_for_status()
    return {"session": session, "status": "LOGGED_OUT"}


async def delete_session(session: str) -> dict:
    response = await _waha_request("DELETE", f"/api/sessions/{session}")
    if response.status_code == 404:
        return {"session": session, "status": "NOT_FOUND"}
    response.raise_for_status()
    return {"session": session, "status": "DELETED"}


def normalize_phone(phone: str) -> str:
    digits = phone_digits(phone)
    return f"{digits}@c.us"


def phone_digits(phone: str) -> str:
    digits = "".join(ch for ch in (phone or "") if ch.isdigit())
    if len(digits) == 10:
        return f"52{digits}"
    if digits.startswith("052"):
        return digits[1:]
    return digits


async def send_text_result(phone: Optional[str], text: str, session: Optional[str] = None) -> tuple[bool, str]:
    if not settings.WAHA_ENABLED or not settings.WAHA_BASE_URL or not phone:
        return False, "WAHA está deshabilitado, sin URL o sin teléfono"
    selected_session = session or settings.WAHA_MASTER_SESSION
    payload = {"chatId": normalize_phone(phone), "text": text, "session": selected_session}
    api_key = settings.WAHA_API_KEY_PLAIN or settings.WAHA_API_KEY
    # Nunca enviar el hash sha512 como si fuera la clave plana.
    if api_key.startswith("sha512:"):
        api_key = ""
    headers = {"X-Api-Key": api_key} if api_key else {}
    try:
        async with httpx.AsyncClient(timeout=settings.WAHA_TIMEOUT_SECONDS) as client:
            check = await client.get(
                f"{settings.WAHA_BASE_URL.rstrip('/')}/api/contacts/check-exists",
                params={"phone": phone_digits(phone), "session": selected_session},
                headers=headers,
            )
            if not check.is_success:
                detail = check.text[:500]
                return False, f"No se pudo validar el número en WAHA (HTTP {check.status_code}): {detail}"
            contact = check.json()
            if contact.get("numberExists") is False:
                return False, "El número no está registrado en WhatsApp"
            chat_id = contact.get("chatId") or contact.get("pn") or normalize_phone(phone)
            response = await client.post(
                f"{settings.WAHA_BASE_URL.rstrip('/')}/api/sendText",
                json={"chatId": chat_id, "text": text, "session": selected_session}, headers=headers,
            )
            if response.is_success:
                return True, ""
            detail = response.text[:500]
            logger.error("WAHA rechazó el envío (%s): %s", response.status_code, detail)
            return False, f"WAHA respondió HTTP {response.status_code}: {detail}"
    except Exception as exc:
        logger.exception("No se pudo enviar WhatsApp a %s usando sesión %s", phone, selected_session)
        return False, f"No se pudo conectar con WAHA: {exc}"


async def send_text(phone: Optional[str], text: str, session: Optional[str] = None) -> bool:
    sent, _ = await send_text_result(phone, text, session)
    return sent
