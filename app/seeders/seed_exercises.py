"""Seeder del catálogo de ejercicios.

Inserta los ejercicios de `exercise_data.py` de forma idempotente:
- Si el ejercicio ya existe (mismo nombre), no se duplica.
- Si existe pero le faltan datos, se actualizan los campos.
"""
import logging
from app.models.routine import Exercise
from app.seeders.exercise_data import EXERCISES

logger = logging.getLogger("gymcontrol.seeders")


async def seed_exercises() -> int:
    created = 0
    updated = 0
    for data in EXERCISES:
        existing = await Exercise.get_or_none(name=data["name"])
        if existing:
            changed = False
            for field, value in data.items():
                if getattr(existing, field, None) != value:
                    setattr(existing, field, value)
                    changed = True
            if changed:
                await existing.save(update_fields=list(data.keys()))
                updated += 1
        else:
            await Exercise.create(**data)
            created += 1

    logger.info(f"🌱 Ejercicios sembrados: {created} nuevos, {updated} actualizados, {len(EXERCISES)} en catálogo")
    return created
