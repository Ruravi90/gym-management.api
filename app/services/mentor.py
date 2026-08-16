"""Servicio del mentor IA de fitness.

Usa una API de chat completions compatible con OpenAI (OpenAI, Groq, OpenRouter,
Ollama, etc.) configurable vía variables de entorno. Si no hay API key configurada,
responde con una respuesta por reglas para que la función no rompa.
"""
import httpx
from app.config import settings


SYSTEM_PROMPT = (
    "Eres 'FitMentor', un coach de fitness motivador y práctico que habla español. "
    "Ayudas a clientes de un gimnasio a seguir sus rutinas: aconsejas sobre técnica, "
    "series, repeticiones, descansos, progresión de peso y constancia. "
    "Respondes de forma breve (máx. 150 palabras), con tono motivador y directo. "
    "Si te preguntan por algo fuera de fitness/entrenamiento, redirige amablemente al tema."
)


WEEKLY_CHECKIN_PROMPT = (
    "Eres 'FitMentor', un coach de fitness motivador que habla español. "
    "Genera un REPORTE SEMANAL para el cliente con base en sus medidas corporales, su rutina "
    "y sus sesiones de la última semana. Estructura tu respuesta así:\n"
    "1) 📏 Resumen de medidas: cambios respecto a la semana anterior (qué mejoró y qué no).\n"
    "2) 🏋️ Adherencia a la rutina: cuántas sesiones hizo y cómo va su constancia.\n"
    "3) 💡 Recomendaciones: 2-3 acciones concretas y realistas para la próxima semana "
    "(ajustes de peso, series, descanso o hábitos).\n"
    "Máximo 220 palabras, tono motivador y directo, sin relleno."
)


async def _call_llm(system_prompt: str, context: str, user_message: str, max_tokens: int = 300) -> dict:
    """Llamada base a la API compatible con OpenAI. Devuelve reply + provider."""
    if not settings.OPENAI_API_KEY:
        return {
            "reply": (
                "⚠️ El mentor IA no está configurado todavía. "
                "Pide al administrador que agregue la variable OPENAI_API_KEY al backend. "
                "Mientras tanto, aquí va un consejo de oro: prioriza la técnica sobre el peso y "
                "registra cada serie para ver tu progreso. ¡Tú puedes! 💪"
            ),
            "provider": None,
        }

    url = f"{settings.OPENAI_BASE_URL.rstrip('/')}/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }
    messages = [{"role": "system", "content": system_prompt}]
    if context:
        messages.append({
            "role": "system",
            "content": "Contexto del cliente (rutina, progreso y medidas):\n" + context,
        })
    messages.append({"role": "user", "content": user_message})

    payload = {
        "model": settings.OPENAI_MODEL,
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": max_tokens,
    }

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
            reply = data["choices"][0]["message"]["content"].strip()
            return {"reply": reply, "provider": settings.OPENAI_MODEL}
    except Exception as e:  # noqa: BLE001 - respuesta amigable ante cualquier fallo
        return {
            "reply": (
                "Lo siento, tu mentor IA no pudo conectarse en este momento "
                f"(error: {type(e).__name__}). Inténtalo de nuevo en unos segundos."
            ),
            "provider": None,
        }


async def mentor_chat(message: str, context: str = "") -> dict:
    """Envía el mensaje al LLM con el contexto del cliente. Devuelve la respuesta del mentor."""
    return await _call_llm(SYSTEM_PROMPT, context, message, max_tokens=300)


async def weekly_checkin(context: str = "") -> dict:
    """Genera el reporte semanal del cliente con medidas + rutina + sesiones."""
    return await _call_llm(
        WEEKLY_CHECKIN_PROMPT,
        context,
        "Genera mi reporte semanal de progreso.",
        max_tokens=500,
    )


def build_client_context(client, routines, recent_sessions, measurements=None) -> str:
    """Construye un resumen del estado del cliente para dar contexto al LLM."""
    lines = [f"Cliente: {client.name}", f"Tipo de membresía: {client.membership_type or 'N/A'}"]

    active = [r for r in routines if r.is_active]
    if active:
        lines.append("Rutinas activas:")
        for r in active[:3]:
            day_names = ", ".join(d.name for d in r.days) if r.days else "sin días definidos"
            lines.append(f"  - {r.name} ({day_names})")
    else:
        lines.append("Sin rutinas activas.")

    if recent_sessions:
        lines.append("Sesiones recientes:")
        for s in recent_sessions[:5]:
            completed = sum(1 for sl in s.set_logs if sl.completed)
            total = len(s.set_logs)
            lines.append(
                f"  - {s.date} {s.status} ({completed}/{total} series registradas)"
            )

    if measurements:
        lines.append("Medidas corporales (cm, deltas vs registro anterior):")
        for m in measurements[:4]:
            parts = [f"  - {m.date}:"]
            for label, field in (
                ("peso(kg)", "weight_kg"),
                ("cintura", "waist_cm"),
                ("abdomen bajo", "abdomen_low_cm"),
                ("pierna", "thigh_cm"),
                ("brazo relajado", "arm_relaxed_cm"),
                ("brazo flexionado", "arm_flexed_cm"),
            ):
                value = getattr(m, field, None)
                delta = getattr(m, f"delta_{field}", None)
                if value is not None:
                    if delta is not None:
                        parts.append(f"{label} {value} ({delta:+})")
                    else:
                        parts.append(f"{label} {value}")
            lines.append(", ".join(parts))

    return "\n".join(lines)
