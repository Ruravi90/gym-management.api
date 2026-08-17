"""Servicio del mentor IA de fitness.

Usa una API de chat completions compatible con OpenAI (OpenAI, Groq, OpenRouter,
Ollama, etc.) configurable vía variables de entorno. Si no hay API key configurada,
responde con una respuesta por reglas para que la función no rompa.
"""
import json
import logging
import re
import unicodedata
from typing import List, Optional

import httpx
from app.config import settings

logger = logging.getLogger(__name__)


BODY_TYPE_INFO = {
    "ectomorph": "Delgado, metabolismo rápido. Series pesadas 6-10 reps, poco cardio.",
    "mesomorph": "Atlético, gana músculo fácil. 8-12 reps, equilibrio fuerza/hipertrofia.",
    "endomorph": "Tiende a acumular grasa. 10-15 reps, cardio extra, descansos cortos.",
}


ROUTINE_GENERATION_PROMPT = (
    "Coach de fitness. Diseña rutinas semanales en ESPAÑOL.\n"
    "REGLAS:\n"
    "- Usa SOLO ejercicios de la lista disponible (nombre EXACTO).\n"
    "- Exactamente {days_per_week} día(s), 4-6 ejercicios por día.\n"
    "- Adapta series/reps/descanso al tipo de cuerpo y objetivo.\n"
    "- Responde SOLO JSON válido:\n"
    '{"name":"Mi rutina X días","description":"breve",'
    '"days":[{"name":"Día 1 - ...","exercises":'
    '[{"exercise":"Nombre","sets":4,"reps":"8-12","rest_seconds":90,"notes":"nota"}]}]}'
)


WEEKLY_CHECKIN_PROMPT = (
    "Coach de fitness. Genera REPORTE SEMANAL en español con markdown.\n"
    "Estructura:\n"
    "1) 📏 **Medidas**: cambios vs semana anterior.\n"
    "2) 🏋️ **Adherencia**: sesiones hechas y constancia.\n"
    "3) 💡 **Recomendaciones**: 2-3 acciones concretas.\n"
    "4) 🔄 **¿Cambiar rutina?**: continuar o considerar cambio (si 4+ semanas sin progreso).\n"
    "Máx 200 palabras, tono motivador."
)

MONTHLY_REPORT_PROMPT = (
    "Coach de fitness. Genera REPORTE MENSUAL en español con markdown.\n"
    "Tienes 4 semanas de datos. Analiza la tendencia completa.\n"
    "Estructura:\n"
    "1) 📊 **Resumen del mes**: peso, medidas y cambios acumulados.\n"
    "2) 📈 **Tendencia**: mejoró, empeoró o se mantuvo en cada métrica.\n"
    "3) 🏋️ **Constancia**: total de sesiones, regularidad.\n"
    "4) 💡 **Recomendaciones**: 3-4 acciones para el próximo mes.\n"
    "5) 🔄 **¿Cambiar rutina?**: recomendación fundamentada (continuar/cambiar/ajustar).\n"
    "Sé específico con números. Máx 300 palabras, tono motivador."
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

    # Tolerar que la base ya incluya "/chat/completions" (p. ej. si el usuario
    # copió la URL completa del endpoint en OPENAI_BASE_URL)
    base = settings.OPENAI_BASE_URL.rstrip("/")
    url = base if base.endswith("/chat/completions") else f"{base}/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
        "Content-Type": "application/json",
        # Headers recomendados por OpenRouter para identificar la app
        "HTTP-Referer": "https://gymcontrol.app",
        "X-Title": "GymControl FitMentor",
    }
    messages = [{"role": "system", "content": system_prompt}]
    if context:
        messages.append({
            "role": "system",
            "content": "Contexto:\n" + context,
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
        logger.exception("LLM call failed")
        return {
            "reply": (
                "No pude conectarme con la IA en este momento. "
                "Inténtalo de nuevo en unos segundos. 💪"
            ),
            "provider": None,
        }


async def weekly_checkin(context: str = "") -> dict:
    """Genera el reporte semanal del cliente con medidas + rutina + sesiones."""
    return await _call_llm(
        WEEKLY_CHECKIN_PROMPT,
        context,
        "Genera mi reporte semanal de progreso.",
        max_tokens=400,
    )


async def monthly_report(context: str = "") -> dict:
    """Genera el reporte mensual del cliente con tendencia completa."""
    return await _call_llm(
        MONTHLY_REPORT_PROMPT,
        context,
        "Genera mi reporte mensual de progreso.",
        max_tokens=500,
    )


# =====================================================================
# Generación de rutinas con IA
# =====================================================================
def _parse_json_reply(text: str) -> Optional[dict]:
    """Extrae el primer objeto JSON de la respuesta del LLM (tolera markdown y texto extra)."""
    if not text:
        return None
    cleaned = text.strip()
    # Quitar cercos de código markdown ```json ... ```
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", cleaned, flags=re.IGNORECASE)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass
    # Buscar el primer { ... } balanceado
    start = cleaned.find("{")
    if start == -1:
        return None
    depth = 0
    for i in range(start, len(cleaned)):
        ch = cleaned[i]
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                try:
                    return json.loads(cleaned[start:i + 1])
                except json.JSONDecodeError:
                    return None
    return None


def _norm(s: Optional[str]) -> str:
    """Normaliza un texto: minúsculas, sin tildes y sin símbolos, para comparar nombres."""
    s = unicodedata.normalize("NFKD", s or "")
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9 ]", "", s.lower()).strip()


def match_exercise(name: str, catalog: List) -> Optional[dict]:
    """Busca un ejercicio del catálogo por nombre (exacto, contención o tokens)."""
    n = _norm(name)
    if not n:
        return None
    for ex in catalog:
        if _norm(ex.name) == n:
            return ex
    for ex in catalog:
        en = _norm(ex.name)
        if n in en or en in n:
            return ex
    toks = set(n.split())
    for ex in catalog:
        if toks and toks <= set(_norm(ex.name).split()):
            return ex
    return None


def _bmi_category(bmi: Optional[float]) -> Optional[str]:
    if bmi is None:
        return None
    if bmi < 18.5:
        return f"{bmi} (bajo peso)"
    if bmi < 25:
        return f"{bmi} (normal)"
    if bmi < 30:
        return f"{bmi} (sobrepeso)"
    return f"{bmi} (obesidad)"


async def generate_routine_plan(
    body_type: str,
    goal: str,
    days_per_week: int,
    equipment: Optional[str],
    experience: Optional[str],
    duration_minutes: Optional[int],
    catalog: List,
    height_cm: Optional[float] = None,
    weight_kg: Optional[float] = None,
    age: Optional[int] = None,
    sex: Optional[str] = None,
    daily_activity: Optional[str] = None,
    injuries: Optional[str] = None,
) -> dict:
    """Pide al LLM una rutina semanal en JSON y devuelve {"ok", "plan"|, "reply"}.

    Recibe TODO el intake del instructor (perfil físico + preferencias) para
    que la rutina se adapte a los objetivos y limitaciones del cliente.
    """
    if not settings.OPENAI_API_KEY:
        return {
            "ok": False,
            "reply": (
                "⚠️ El mentor IA no está configurado todavía. Pide al administrador que "
                "agregue OPENAI_API_KEY al backend y podré diseñar tu rutina personalizada."
            ),
        }

    body_info = BODY_TYPE_INFO.get(body_type, BODY_TYPE_INFO["mesomorph"])
    bmi = None
    if height_cm and weight_kg:
        m = height_cm / 100.0
        bmi = round(float(weight_kg) / (m * m), 1)

    profile_parts = [f"{body_type}. {body_info}"]
    if age:
        profile_parts.append(f"{age}a")
    if sex:
        profile_parts.append(sex)
    if height_cm and weight_kg:
        profile_parts.append(f"{height_cm}cm/{weight_kg}kg")
    if bmi is not None:
        profile_parts.append(f"IMC:{_bmi_category(bmi)}")
    if daily_activity:
        profile_parts.append(f"act:{daily_activity}")
    if injuries:
        profile_parts.append(f"LESIONES:{injuries}")

    user_message = (
        f"Perfil: {', '.join(profile_parts)}. "
        f"Objetivo:{goal or 'general'}. Días:{days_per_week}. "
        f"Equipo:{equipment or 'gimnasio'}. Exp:{experience or 'principiante'}. "
        f"Duración:{duration_minutes or 60}min.\n"
        f"Ejercicios (nombres EXACTOS):\n{catalog_lines}"
    )

    result = await _call_llm(ROUTINE_GENERATION_PROMPT, "", user_message, max_tokens=1200)
    plan = _parse_json_reply(result.get("reply", ""))
    if not plan or not isinstance(plan, dict) or not plan.get("days"):
        return {
            "ok": False,
            "reply": (
                "🤔 No pude estructurar tu rutina esta vez. Inténtalo de nuevo en unos "
                "segundos o reformula tu objetivo."
            ),
        }

    # Normalizar el plan: números y campos por defecto
    days = []
    for day in plan.get("days", []):
        exercises = []
        for i, ex in enumerate(day.get("exercises", [])):
            matched = match_exercise(ex.get("exercise", ""), catalog)
            if not matched:
                continue
            exercises.append(
                {
                    "exercise_id": matched.id,
                    "sets": int(ex.get("sets") or 3),
                    "reps": str(ex.get("reps") or "10"),
                    "rest_seconds": int(ex.get("rest_seconds") or 60),
                    "notes": ex.get("notes") or None,
                    "order": i,
                }
            )
        if exercises:
            days.append(
                {
                    "name": day.get("name") or f"Día {len(days) + 1}",
                    "day_of_week": None,
                    "order": len(days),
                    "exercises": exercises,
                }
            )

    if not days:
        return {
            "ok": False,
            "reply": "😅 No encontré ejercicios de mi catálogo en la propuesta. Inténtalo de nuevo.",
        }

    plan["name"] = plan.get("name") or f"Mi rutina de {days_per_week} días"
    plan["days"] = days
    return {"ok": True, "plan": plan, "provider": result.get("provider")}


def build_client_context(
    client,
    routines,
    recent_sessions,
    measurements=None,
    body_type=None,
    height_cm=None,
    age=None,
    weight_kg=None,
) -> str:
    """Construye un resumen del estado del cliente para dar contexto al LLM."""
    lines = []
    if body_type:
        lines.append(f"Cuerpo: {body_type}. {BODY_TYPE_INFO.get(body_type, '')}")
    if age:
        lines.append(f"Edad: {age}a")
    if height_cm and weight_kg:
        m = height_cm / 100.0
        bmi = round(float(weight_kg) / (m * m), 1)
        lines.append(f"Altura: {height_cm}cm, Peso: {weight_kg}kg, IMC: {_bmi_category(bmi)}")

    active = [r for r in routines if r.is_active]
    if active:
        for r in active[:2]:
            days = ", ".join(d.name for d in r.days[:4]) if r.days else "sin días"
            lines.append(f"Rutina: {r.name} ({days})")
    else:
        lines.append("Sin rutina activa")

    if recent_sessions:
        done = sum(1 for s in recent_sessions if s.status == "completed")
        lines.append(f"Sesiones último mes: {done}/{len(recent_sessions)}")

    if measurements:
        last = measurements[0]
        parts = []
        for label, field in (
            ("peso", "weight_kg"),
            ("cintura", "waist_cm"),
            ("abdomen", "abdomen_low_cm"),
            ("pierna", "thigh_cm"),
            ("brazo", "arm_relaxed_cm"),
        ):
            v = getattr(last, field, None)
            d = getattr(last, f"delta_{field}", None)
            if v is not None:
                parts.append(f"{label}:{v}{f'({d:+})' if d else ''}")
        if parts:
            lines.append(f"Medidas {last.date}: {', '.join(parts)}")
        if len(measurements) > 1:
            prev = measurements[1]
            pw = getattr(prev, "weight_kg", None)
            if pw and last.weight_kg:
                diff = float(last.weight_kg) - float(pw)
                lines.append(f"Peso vs semana ant: {diff:+.1f}kg")

    return "; ".join(lines)
