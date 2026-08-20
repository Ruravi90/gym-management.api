from app.models.gamification import AchievementDefinition, CriteriaType


ACHIEVEMENT_DEFINITIONS = [
    # Por asistencia
    {
        "key": "first_checkin",
        "name": "Primera Visita",
        "description": "Registra tu primer check-in en el gym",
        "icon": "🏋️",
        "xp_reward": 25,
        "criteria_type": CriteriaType.CHECKINS_TOTAL,
        "criteria_value": 1,
    },
    {
        "key": "regular_10",
        "name": "Regular",
        "description": "Acumula 10 check-ins en el gym",
        "icon": "💪",
        "xp_reward": 50,
        "criteria_type": CriteriaType.CHECKINS_TOTAL,
        "criteria_value": 10,
    },
    {
        "key": "dedicated_50",
        "name": "Dedicado",
        "description": "Acumula 50 check-ins en el gym",
        "icon": "🔥",
        "xp_reward": 200,
        "criteria_type": CriteriaType.CHECKINS_TOTAL,
        "criteria_value": 50,
    },
    {
        "key": "legend_100",
        "name": "Leyenda del Gym",
        "description": "Acumula 100 check-ins en el gym",
        "icon": "👑",
        "xp_reward": 500,
        "criteria_type": CriteriaType.CHECKINS_TOTAL,
        "criteria_value": 100,
    },
    # Por racha
    {
        "key": "streak_3",
        "name": "Tres Días Seguidos",
        "description": "Asiste 3 días consecutivos al gym",
        "icon": "⚡",
        "xp_reward": 30,
        "criteria_type": CriteriaType.STREAK_DAYS,
        "criteria_value": 3,
    },
    {
        "key": "streak_7",
        "name": "Semana Perfecta",
        "description": "Asiste 7 días consecutivos al gym",
        "icon": "🌟",
        "xp_reward": 100,
        "criteria_type": CriteriaType.STREAK_DAYS,
        "criteria_value": 7,
    },
    {
        "key": "streak_14",
        "name": "Imparable",
        "description": "Asiste 14 días consecutivos al gym",
        "icon": "🚀",
        "xp_reward": 200,
        "criteria_type": CriteriaType.STREAK_DAYS,
        "criteria_value": 14,
    },
    {
        "key": "streak_30",
        "name": "Mes Completo",
        "description": "Asiste 30 días consecutivos al gym",
        "icon": "🏆",
        "xp_reward": 500,
        "criteria_type": CriteriaType.STREAK_DAYS,
        "criteria_value": 30,
    },
    # Por Kaizen
    {
        "key": "first_victory",
        "name": "Primera Victoria",
        "description": "Registra tu primera victoria en Kaizen",
        "icon": "🎯",
        "xp_reward": 25,
        "criteria_type": CriteriaType.KAIZEN_VICTORIES,
        "criteria_value": 1,
    },
    {
        "key": "victory_25",
        "name": "Guerrero",
        "description": "Acumula 25 victorias en Kaizen",
        "icon": "⚔️",
        "xp_reward": 150,
        "criteria_type": CriteriaType.KAIZEN_VICTORIES,
        "criteria_value": 25,
    },
    {
        "key": "victory_100",
        "name": "Maestro Kaizen",
        "description": "Acumula 100 victorias en Kaizen",
        "icon": "🧙",
        "xp_reward": 500,
        "criteria_type": CriteriaType.KAIZEN_VICTORIES,
        "criteria_value": 100,
    },
    # Por entrenamiento
    {
        "key": "first_workout",
        "name": "Primer Entreno",
        "description": "Completa tu primera sesión de entrenamiento",
        "icon": "🏃",
        "xp_reward": 25,
        "criteria_type": CriteriaType.WORKOUTS_COMPLETED,
        "criteria_value": 1,
    },
    {
        "key": "workout_10",
        "name": "En Forma",
        "description": "Completa 10 sesiones de entrenamiento",
        "icon": "🏅",
        "xp_reward": 100,
        "criteria_type": CriteriaType.WORKOUTS_COMPLETED,
        "criteria_value": 10,
    },
    {
        "key": "workout_25",
        "name": "Fuerza Bruta",
        "description": "Completa 25 sesiones de entrenamiento",
        "icon": "🦾",
        "xp_reward": 200,
        "criteria_type": CriteriaType.WORKOUTS_COMPLETED,
        "criteria_value": 25,
    },
    {
        "key": "workout_100",
        "name": "Máquina de Entreno",
        "description": "Completa 100 sesiones de entrenamiento",
        "icon": "💎",
        "xp_reward": 500,
        "criteria_type": CriteriaType.WORKOUTS_COMPLETED,
        "criteria_value": 100,
    },
    # Por repeticiones
    {
        "key": "sets_100",
        "name": "Cien Repeticiones",
        "description": "Registra 100 series en total",
        "icon": "💯",
        "xp_reward": 50,
        "criteria_type": CriteriaType.SETS_TOTAL,
        "criteria_value": 100,
    },
    {
        "key": "sets_500",
        "name": "500 Repeticiones",
        "description": "Registra 500 series en total",
        "icon": "🎯",
        "xp_reward": 300,
        "criteria_type": CriteriaType.SETS_TOTAL,
        "criteria_value": 500,
    },
    # Por medidas
    {
        "key": "first_measurement",
        "name": "Primera Medición",
        "description": "Registra tus primeras medidas corporales",
        "icon": "📏",
        "xp_reward": 25,
        "criteria_type": CriteriaType.MEASUREMENTS_TOTAL,
        "criteria_value": 1,
    },
    {
        "key": "monthly_tracking",
        "name": "Seguimiento Mensual",
        "description": "Registra medidas 4 veces (1 por semana)",
        "icon": "📊",
        "xp_reward": 100,
        "criteria_type": CriteriaType.MEASUREMENTS_TOTAL,
        "criteria_value": 4,
    },
]


async def seed_achievements():
    for ach in ACHIEVEMENT_DEFINITIONS:
        existing = await AchievementDefinition.get_or_none(key=ach["key"])
        if not existing:
            await AchievementDefinition.create(**ach)
