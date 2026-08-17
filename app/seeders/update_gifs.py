# -*- coding: utf-8 -*-
"""Función reutilizable para actualizar gif_urls desde el catálogo.

Puede usarse como:
  - Script standalone: venv/bin/python -m app.seeders.update_gifs
  - Importado desde main.py (ya tiene Tortoise init)
"""
import logging
from app.models.routine import Exercise
from app.seeders.gif_catalog import GIF_CATALOG

logger = logging.getLogger("gymcontrol.seeders")


async def update_gifs() -> int:
    """Actualiza gif_urls de todos los ejercicios desde GIF_CATALOG.

    Retorna el número de ejercicios actualizados.
    """
    updated = 0
    exercises = await Exercise.all().only("id", "name", "gif_urls")
    for exercise in exercises:
        name_lower = exercise.name.lower().strip()
        if name_lower in GIF_CATALOG:
            urls = GIF_CATALOG[name_lower]
            exercise.gif_urls = urls
            await exercise.save(update_fields=["gif_urls"])
            updated += 1

    logger.info(f"🎬 GIFs actualizados: {updated}/{len(exercises)} ejercicios")
    return updated


# --- Script standalone ---
if __name__ == "__main__":
    import asyncio
    import sys
    import os
    from dotenv import load_dotenv

    load_dotenv()
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

    from tortoise import Tortoise
    from app.config import settings

    async def _main():
        await Tortoise.init(
            db_url=settings.DATABASE_URL,
            modules={"models": ["app.models.routine"]},
        )
        await update_gifs()
        await Tortoise.close_connections()

    asyncio.run(_main())
