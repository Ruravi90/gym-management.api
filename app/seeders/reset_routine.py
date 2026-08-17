# -*- coding: utf-8 -*-
"""Script para eliminar la rutina de un usuario y actualizar GIFs.

Uso: venv/bin/python -m app.seeders.reset_routine
"""
import asyncio
import sys
import os
from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from tortoise import Tortoise
from app.config import settings


async def reset_routine():
    await Tortoise.init(
        db_url=settings.DATABASE_URL,
        modules={"models": [
            "app.models.user", "app.models.client", "app.models.routine",
            "app.models.measurement", "app.models.mentor_message",
        ]},
    )

    from app.models.user import User
    from app.models.client import Client
    from app.models.routine import Routine, RoutineDay, RoutineExercise, WorkoutSession, SetLog
    from app.models.mentor_message import MentorMessage
    from app.seeders.gif_catalog import GIF_CATALOG

    email = "ruravi@icloud.com"
    user = await User.get_or_none(email=email)
    if not user:
        print(f"❌ Usuario {email} no encontrado")
        await Tortoise.close_connections()
        return

    client = await Client.get_or_none(user_id=user.id)
    if not client:
        print(f"❌ Cliente no encontrado para {email}")
        await Tortoise.close_connections()
        return

    print(f"👤 Usuario: {user.name} ({email})")
    print(f"   Client ID: {client.id}")

    # Eliminar rutinas y dependencias
    routines = await Routine.filter(client_id=client.id)
    for routine in routines:
        days = await RoutineDay.filter(routine_id=routine.id)
        for day in days:
            await RoutineExercise.filter(day_id=day.id).delete()
            await WorkoutSession.filter(day_id=day.id).delete()
        await RoutineDay.filter(routine_id=routine.id).delete()
        await routine.delete()
        print(f"   🗑️ Rutina eliminada: {routine.name}")

    # Eliminar sesiones huérfanas
    sessions = await WorkoutSession.filter(client_id=client.id)
    for session in sessions:
        await SetLog.filter(session_id=session.id).delete()
        await session.delete()
        print(f"   🗑️ Sesión eliminada: {session.date}")

    # Eliminar mensajes del mentor
    deleted_msgs = await MentorMessage.filter(client_id=client.id).delete()
    print(f"   🗑️ {deleted_msgs} mensajes del mentor eliminados")

    # Resetear fechas de reportes
    client.last_weekly_checkin_at = None
    client.last_monthly_report_at = None
    await client.save(update_fields=["last_weekly_checkin_at", "last_monthly_report_at"])
    print(f"   🔄 Fechas de reportes reseteadas")

    # Actualizar GIFs de todos los ejercicios
    from app.models.routine import Exercise
    updated = 0
    for exercise in await Exercise.all():
        name_lower = exercise.name.lower().strip()
        if name_lower in GIF_CATALOG:
            urls = GIF_CATALOG[name_lower]
            exercise.gif_urls = urls
            await exercise.save(update_fields=["gif_urls"])
            updated += 1

    total = await Exercise.all().count()
    print(f"\n🎬 GIFs actualizados: {updated}/{total} ejercicios")
    print(f"✅ Listo! Puedes regenerar la rutina desde la app.")

    await Tortoise.close_connections()


if __name__ == "__main__":
    asyncio.run(reset_routine())
