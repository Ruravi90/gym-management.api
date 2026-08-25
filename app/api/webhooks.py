import hmac
import logging

from fastapi import APIRouter, Header, HTTPException, Request

from app.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/waha")
async def waha_webhook(
    request: Request,
    x_webhook_secret: str | None = Header(default=None, alias="X-Webhook-Secret"),
):
    """Recibe eventos de WAHA a través del proxy público /api/webhooks/waha."""
    if settings.WAHA_WEBHOOK_SECRET and not hmac.compare_digest(
        x_webhook_secret or "", settings.WAHA_WEBHOOK_SECRET
    ):
        raise HTTPException(status_code=401, detail="Webhook no autorizado")

    payload = await request.json()
    event = payload.get("event") or payload.get("type") or "unknown"
    session = payload.get("session") or "unknown"
    logger.info("WAHA webhook recibido: evento=%s sesión=%s", event, session)
    return {"ok": True}
