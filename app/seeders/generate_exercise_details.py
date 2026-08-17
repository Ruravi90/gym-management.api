# -*- coding: utf-8 -*-
"""Script para generar tips, common_mistakes y modifications de ejercicios usando IA.

Uso: venv/bin/python -m app.seeders.generate_exercise_details
"""
import asyncio
import json
import os
import sys
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from tortoise import Tortoise
from app.config import settings
from app.models.routine import Exercise

DETAIL_PROMPT = (
    "Eres un preparador físico experto. Para el ejercicio dado, genera en español:\n"
    "1) tips: un tip práctico para mejorar la ejecución (1-2 oraciones)\n"
    "2) common_mistakes: un error común a evitar (1-2 oraciones)\n"
    "3) modifications: una variante más fácil o más difícil (1-2 oraciones)\n"
    "Responde SOLO con JSON válido: {\"tips\":\"...\",\"common_mistakes\":\"...\",\"modifications\":\"...\"}"
)


async def generate_details():
    await Tortoise.init(
        db_url=settings.DATABASE_URL,
        modules={"models": [
            "app.models.user", "app.models.client", "app.models.routine",
            "app.models.measurement", "app.models.mentor_message",
        ]},
    )

    if not settings.OPENAI_API_KEY:
        print("❌ OPENAI_API_KEY no configurada")
        await Tortoise.close_connections()
        return

    import httpx

    base = settings.OPENAI_BASE_URL.rstrip("/")
    url = base if base.endswith("/chat/completions") else f"{base}/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }

    exercises = await Exercise.all().only("id", "name", "instructions", "tips", "common_mistakes", "modifications")
    updated = 0
    skipped = 0

    for ex in exercises:
        # Saltar si ya tiene los 3 campos
        if ex.tips and ex.common_mistakes and ex.modifications:
            skipped += 1
            continue

        print(f"  🔄 {ex.name}...", end=" ", flush=True)

        user_msg = (
            f"Ejercicio: {ex.name}\n"
            f"Instrucciones actuales: {ex.instructions or 'N/A'}"
        )

        payload = {
            "model": settings.OPENAI_MODEL,
            "messages": [
                {"role": "system", "content": DETAIL_PROMPT},
                {"role": "user", "content": user_msg},
            ],
            "temperature": 0.7,
            "max_tokens": 200,
        }

        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.post(url, headers=headers, json=payload)
                resp.raise_for_status()
                data = resp.json()
                reply = data["choices"][0]["message"]["content"].strip()

                # Parse JSON
                cleaned = reply.strip()
                if cleaned.startswith("```"):
                    cleaned = cleaned.split("\n", 1)[1].rsplit("```", 1)[0].strip()
                details = json.loads(cleaned)

                ex.tips = details.get("tips")
                ex.common_mistakes = details.get("common_mistakes")
                ex.modifications = details.get("modifications")
                await ex.save(update_fields=["tips", "common_mistakes", "modifications"])
                updated += 1
                print("✅")
        except Exception as e:
            print(f"❌ {e}")

    print(f"\n📊 Resultado: {updated} actualizados, {skipped} ya tenían datos, {len(exercises)} total")
    await Tortoise.close_connections()


if __name__ == "__main__":
    asyncio.run(generate_details())
