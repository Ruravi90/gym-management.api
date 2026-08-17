"""Seeder del catálogo de ejercicios.

Inserta los ejercicios de `exercise_data.py` de forma idempotente:
- Si el ejercicio ya existe (mismo nombre), no se duplica.
- Si existe pero le faltan datos, se actualizan los campos.
Solo se persisten los campos que existen en el modelo Exercise (p. ej.
`category` en los datos de origen se omite, ya que el modelo usa
`muscle_group`/`body_part`).
"""
import logging
from app.models.routine import Exercise
from app.seeders.exercise_data import EXERCISES

logger = logging.getLogger("gymcontrol.seeders")

# Campos válidos del modelo (excluye pk y timestamps automáticos)
MODEL_FIELDS = set(Exercise._meta.fields_map.keys()) - {"id", "created_at", "updated_at"}


def _clean(data: dict) -> dict:
    """Devuelve solo los campos que existen en el modelo Exercise."""
    return {k: v for k, v in data.items() if k in MODEL_FIELDS}


async def seed_exercises() -> int:
    created = 0
    updated = 0
    for data in EXERCISES:
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

    logger.info(f"🌱 Ejercicios sembrados: {created} nuevos, {updated} actualizados, {len(EXERCISES)} en catálogo")
    return created
