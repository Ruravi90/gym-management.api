from typing import List, Optional
from datetime import date
from app.models.gamification import (
    XpLog,
    AchievementDefinition,
    ClientAchievement,
    WeeklyChallenge,
    ClientChallenge,
    ActionType,
    CriteriaType,
)
from app.services.gamification import GamificationService

gamification_service = GamificationService()


async def get_progress_summary(client_id: int) -> dict:
    return await gamification_service.get_progress_summary(client_id)


async def get_xp_history(
    client_id: int, limit: int = 20, offset: int = 0
) -> List[dict]:
    return await gamification_service.get_xp_history(client_id, limit, offset)


async def get_achievements_with_status(client_id: int) -> List[dict]:
    return await gamification_service.get_achievements_with_status(client_id)


async def award_xp(
    client_id: int,
    action_type: str,
    base_amount: int,
    description: str,
) -> dict:
    return await gamification_service.award_xp(
        client_id, action_type, base_amount, description
    )


async def update_streak(client_id: int) -> dict:
    return await gamification_service.update_streak(client_id)


async def get_active_challenges(client_id: int) -> List[dict]:
    return await gamification_service.get_active_challenges(client_id)


async def evaluate_challenges(client_id: int) -> List[dict]:
    return await gamification_service.evaluate_challenges(client_id)
