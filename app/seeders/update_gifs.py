# -*- coding: utf-8 -*-
"""Script para actualizar gif_urls de los ejercicios existentes.

Uso: python -m app.seeders.update_gifs
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from tortoise import Tortoise
from app.models.routine import Exercise
from app.seeders.gif_catalog import GIF_CATALOG


async def update_gifs():
    await Tortoise.init(
        db_url="sqlite:///db.sqlite3",
        modules={"models": ["app.models.routine"]},
    )

    updated = 0
    for exercise in await Exercise.all().only("id", "name", "gif_urls"):
        name_lower = exercise.name.lower().strip()
        if name_lower in GIF_CATALOG:
            urls = GIF_CATALOG[name_lower]
            exercise.gif_urls = urls
            await exercise.save(update_fields=["gif_urls"])
            print(f"  ✅ {exercise.name} -> {len(urls)} GIFs")
            updated += 1

    print(f"\nTotal actualizados: {updated}/{await Exercise.all().count()} ejercicios")
    await Tortoise.close_connections()


if __name__ == "__main__":
    asyncio.run(update_gifs())
