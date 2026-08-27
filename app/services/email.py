import asyncio
import logging
import smtplib
from email.message import EmailMessage
from typing import Optional
from app.config import settings

logger = logging.getLogger(__name__)

def _send(to: str, subject: str, body: str) -> None:
    if not settings.SMTP_HOST or not settings.SMTP_FROM:
        raise RuntimeError("SMTP no está configurado")
    message = EmailMessage()
    message["From"], message["To"], message["Subject"] = settings.SMTP_FROM, to, subject
    message.set_content(body)
    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=20) as server:
        if settings.SMTP_TLS:
            server.starttls()
        if settings.SMTP_USER:
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        server.send_message(message)

async def send_password_reset_email(email: Optional[str], name: str, link: str) -> bool:
    if not email:
        return False
    if not settings.SMTP_HOST or not settings.SMTP_FROM:
        logger.warning("SMTP no configurado; se usará WhatsApp como respaldo para %s", email)
        return False
    try:
        await asyncio.to_thread(_send, email, "Restablece tu contraseña de MyGym", f"Hola {name},\n\nRecibimos una solicitud para cambiar tu contraseña. Abre este enlace (válido por 20 minutos):\n\n{link}\n\nSi no solicitaste este cambio, ignora este mensaje.")
        return True
    except Exception:
        logger.exception("No se pudo enviar el correo de recuperación a %s", email)
        return False
