"""Seeder del catálogo de ejercicios.

Inserta los ejercicios de `exercise_data.py` de forma idempotente:
- Si el ejercicio ya existe (mismo nombre), no se duplica.
- Si existe pero le faltan datos, se actualizan los campos.
Solo se persisten los campos que existen en el modelo Exercise (p. ej.
`category` en los datos de origen se omite, ya que el modelo usa
`muscle_group`/`body_part`).
"""
import logging
import os
import httpx
from app.models.routine import Exercise
from app.seeders.exercise_data import EXERCISES

logger = logging.getLogger("gymcontrol.seeders")

REMOTE_CATALOG_URL = os.getenv(
    "EXERCISE_CATALOG_URL",
    "https://cdn.jsdelivr.net/gh/JahelCuadrado/ExerciseGymGifsDB@v1.1.0/api/es/exercises.json",
)

# Campos válidos del modelo (excluye pk y timestamps automáticos)
MODEL_FIELDS = set(Exercise._meta.fields_map.keys()) - {"id", "created_at", "updated_at"}


def _clean(data: dict) -> dict:
    """Devuelve solo los campos que existen en el modelo Exercise."""
    return {k: v for k, v in data.items() if k in MODEL_FIELDS}


async def _remote_exercises() -> list[dict]:
    """Descarga el catálogo ampliado; cualquier fallo deja operativo el catálogo local."""
    try:
        async with httpx.AsyncClient(timeout=20, follow_redirects=True) as client:
            response = await client.get(REMOTE_CATALOG_URL)
            response.raise_for_status()
            payload = response.json()
        return payload.get("exercises", payload) if isinstance(payload, (dict, list)) else []
    except Exception as exc:
        logger.warning("No se pudo sincronizar el catálogo remoto: %s", exc)
        return []


def _remote_to_model(item: dict) -> dict | None:
    name = item.get("name")
    if not name:
        return None
    equipment = item.get("equipment") or "none"
    # El repositorio es un catálogo general; las modalidades especializadas
    # siguen viniendo del seeder propio y no se reclasifican aquí.
    category = (item.get("category") or "").lower()
    name_key = name.lower()
    if equipment in {"bodyweight", "body weight", "gymnastic rings", "pull-up bar", "parallettes"}:
        training_type = "calisthenics"
    elif category == "plyometrics" or any(k in name_key for k in ("snatch", "clean", "thruster", "burpee", "wall ball", "double under")):
        training_type = "crossfit"
    else:
        training_type = "gym"
    return {
        "name": name,
        "training_type": training_type,
        "body_part": item.get("bodyPart") or item.get("body_part"),
        "equipment": equipment,
        "difficulty": "beginner",
        "target": item.get("muscle") or item.get("target"),
        "muscle_group": item.get("muscle") or item.get("target"),
        "secondary_muscles": ", ".join(item.get("secondaryMuscles", [])) or None,
        "instructions": " ".join(item.get("instructions", [])) if isinstance(item.get("instructions"), list) else item.get("instructions"),
        "gif_url": item.get("gifUrl"),
        "gif_urls": [item["gifUrl"]] if item.get("gifUrl") else None,
    }


async def seed_exercises() -> int:
    remote = [_remote_to_model(item) for item in await _remote_exercises()]
    remote = [item for item in remote if item]
    catalog = EXERCISES + remote
    created = 0
    updated = 0
    seen = set()
    for data in catalog:
        key = data["name"].strip().lower()
        if key in seen:
            continue
        seen.add(key)
        clean = _clean(data)
        existing = await Exercise.get_or_none(name=data["name"])
        if existing:
            changed = False
            for field, value in clean.items():
                if getattr(existing, field, None) != value:
                    setattr(existing, field, value)
                    changed = True
            if changed:
                await existing.save(update_fields=list(clean.keys()))
                updated += 1
        else:
            await Exercise.create(**clean)
            created += 1

    logger.info(f"🌱 Ejercicios sembrados: {created} nuevos, {updated} actualizados, {len(seen)} en catálogo")
    return created
