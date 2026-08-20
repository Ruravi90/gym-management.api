from datetime import date, timedelta
from app.models.gamification import WeeklyChallenge, CriteriaType


async def seed_weekly_challenges():
    today = date.today()
    monday = today - timedelta(days=today.weekday())
    sunday = monday + timedelta(days=6)

    existing = await WeeklyChallenge.filter(
        start_date=monday, end_date=sunday
    ).count()
    if existing > 0:
        return

    challenges = [
        {
            "title": "Asiste 3 veces esta semana",
            "description": "Haz check-in al menos 3 veces esta semana",
            "xp_reward": 50,
            "criteria_type": CriteriaType.CHECKINS_TOTAL,
            "criteria_value": 3,
            "start_date": monday,
            "end_date": sunday,
        },
        {
            "title": "Racha de 5 días",
            "description": "Mantén una racha de 5 días consecutivos",
            "xp_reward": 100,
            "criteria_type": CriteriaType.STREAK_DAYS,
            "criteria_value": 5,
            "start_date": monday,
            "end_date": sunday,
        },
        {
            "title": "3 victorias kaizen",
            "description": "Registra al menos 3 victorias en tus hábitos Kaizen",
            "xp_reward": 40,
            "criteria_type": CriteriaType.KAIZEN_VICTORIES,
            "criteria_value": 3,
            "start_date": monday,
            "end_date": sunday,
        },
        {
            "title": "2 sesiones completas",
            "description": "Completa al menos 2 sesiones de entrenamiento",
            "xp_reward": 60,
            "criteria_type": CriteriaType.WORKOUTS_COMPLETED,
            "criteria_value": 2,
            "start_date": monday,
            "end_date": sunday,
        },
        {
            "title": "Registra tus medidas",
            "description": "Actualiza tus medidas corporales esta semana",
            "xp_reward": 30,
            "criteria_type": CriteriaType.MEASUREMENTS_TOTAL,
            "criteria_value": 1,
            "start_date": monday,
            "end_date": sunday,
        },
    ]

    for ch in challenges:
        await WeeklyChallenge.create(**ch)
