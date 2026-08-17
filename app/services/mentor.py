"""Servicio del mentor IA de fitness.

Usa una API de chat completions compatible con OpenAI (OpenAI, Groq, OpenRouter,
Ollama, etc.) configurable vía variables de entorno. Si no hay API key configurada,
responde con una respuesta por reglas para que la función no rompa.
"""
import json
import re
import unicodedata
from typing import List, Optional

import httpx
from app.config import settings


SYSTEM_PROMPT = (
    "Eres 'FitMentor', un coach de fitness motivador y práctico que habla español. "
    "Ayudas a clientes de un gimnasio a seguir sus rutinas: aconsejas sobre técnica, "
    "series, repeticiones, descansos, progresión de peso y constancia. "
    "Respondes de forma breve (máx. 150 palabras), con tono motivador y directo. "
    "Si te preguntan por algo fuera de fitness/entrenamiento, redirige amablemente al tema."
)


BODY_TYPE_INFO = {
    "ectomorph": (
        "Ectomorfo: complexión delgada y metabolismo rápido; te cuesta subir de peso. "
        "Estrategia: más calorías, menos cardio, series pesadas de 6-10 reps y descansos largos."
    ),
    "mesomorph": (
        "Mesomorfo: complexión atlética; ganas músculo y pierdes grasa con facilidad. "
        "Estrategia: equilibrio perfecto entre fuerza e hipertrofia, 8-12 reps, descansos medios."
    ),
    "endomorph": (
        "Endomorfo: tendencia a acumular grasa; ganas músculo fácil pero también peso. "
        "Estrategia: prioriza la definición, 10-15 reps, descansos cortos y cardio extra."
    ),
}


ROUTINE_GENERATION_PROMPT = (
    "Eres 'FitMentor', un coach de fitness que diseña rutinas de entrenamiento semanales. "
    "Debes generar una rutina personalizada en ESPAÑOL considerando el tipo de cuerpo, el "
    "objetivo, los días disponibles, el equipamiento y la experiencia del cliente.\n"
    "REGLAS:\n"
    "- Usa ÚNICAMENTE ejercicios de la lista de ejercicios disponibles que se te da (elige "
    "el nombre EXACTO tal y como aparece en la lista).\n"
    "- Diseña exactamente {days_per_week} día(s) de entrenamiento, con 4 a 6 ejercicios por día.\n"
    "- Distribuye los grupos musculares con sentido (ej. push/pull/legs o torso/pierna).\n"
    "- El número de series, reps y descanso debe adaptarse al tipo de cuerpo y objetivo.\n"
    "- Responde ÚNICAMENTE con un JSON válido (sin texto extra, sin markdown) con este formato:\n"
    '{"name": "Mi rutina X días", "description": "breve descripción", '
    '"days": [{"name": "Día 1 - ...", "exercises": '
    '[{"exercise": "Nombre exacto del ejercicio", "sets": 4, "reps": "8-12", '
    '"rest_seconds": 90, "notes": "nota breve"}]}]}'
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
        bmi = round(weight_kg / (m * m), 1)

    profile_lines = [f"Tipo de cuerpo: {body_type}. {body_info}"]
    if age:
        profile_lines.append(f"Edad: {age} años.")
    if sex:
        profile_lines.append(f"Sexo: {sex}.")
    if height_cm:
        profile_lines.append(f"Altura: {height_cm} cm.")
    if weight_kg:
        profile_lines.append(f"Peso actual: {weight_kg} kg.")
    if bmi is not None:
        profile_lines.append(f"IMC: {_bmi_category(bmi)}.")
    if daily_activity:
        profile_lines.append(f"Actividad diaria fuera del gym: {daily_activity}.")
    if injuries:
        profile_lines.append(
            f"⚠️ LESIONES/LIMITACIONES IMPORTANTES: {injuries}. "
            "Evita a toda costa ejercicios que puedan agravar estas lesiones."
        )

    catalog_lines = "\n".join(
        f"- {ex.name} ({ex.muscle_group or 'general'}, {ex.equipment or 'sin equipo'})"
        for ex in catalog
    )
    user_message = (
        "Perfil del cliente:\n" + "\n".join(profile_lines) + "\n\n"
        f"Objetivo principal: {goal or 'general'}. Días por semana: {days_per_week}. "
        f"Equipamiento: {equipment or 'gimnasio'}. Experiencia: {experience or 'principiante'}. "
        f"Duración por sesión: {duration_minutes or 60} minutos.\n"
        "Actúa como un instructor profesional y diseña una rutina segura y efectiva "
        "para este perfil. Ejercicios disponibles (elige los nombres EXACTOS de aquí):\n"
        f"{catalog_lines}\n"
        "Genera la rutina."
    )

    result = await _call_llm(ROUTINE_GENERATION_PROMPT, "", user_message, max_tokens=1500)
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
    lines = [f"Cliente: {client.name}", f"Tipo de membresía: {client.membership_type or 'N/A'}"]
    if body_type:
        info = BODY_TYPE_INFO.get(body_type)
        lines.append(f"Tipo de cuerpo: {body_type}" + (f" ({info})" if info else ""))
    if age:
        lines.append(f"Edad: {age} años.")
    if height_cm:
        lines.append(f"Altura: {height_cm} cm.")
    if height_cm and weight_kg:
        m = height_cm / 100.0
        bmi = round(weight_kg / (m * m), 1)
        lines.append(f"IMC: {_bmi_category(bmi)}.")

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
