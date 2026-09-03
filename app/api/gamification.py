from fastapi import APIRouter, Depends, Query
from typing import List
from app import crud
from app.utils.auth import get_current_client
from app.models.client import Client

router = APIRouter()


@router.get("/progress")
async def get_progress(client: Client = Depends(get_current_client)):
    return await crud.gamification.get_progress_summary(client.id)


@router.get("/xp-history")
async def get_xp_history(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    client: Client = Depends(get_current_client),
):
    return await crud.gamification.get_xp_history(client.id, limit, offset)


@router.get("/achievements")
async def get_achievements(client: Client = Depends(get_current_client)):
    return await crud.gamification.get_achievements_with_status(client.id)


@router.get("/dashboard")
async def get_dashboard(client: Client = Depends(get_current_client)):
    progress = await crud.gamification.get_progress_summary(client.id)
    recent_xp = await crud.gamification.get_xp_history(client.id, limit=5)
    achievements = await crud.gamification.get_achievements_with_status(client.id)
    challenges = await crud.gamification.get_active_challenges(client.id)

    unlocked = [a for a in achievements if a["earned"]]
    recent_achievements = sorted(
        unlocked, key=lambda a: a.get("earned_date") or "", reverse=True
    )[:5]

    return {
        "progress": progress,
        "recent_xp": recent_xp,
        "recent_achievements": recent_achievements,
        "total_achievements": len(achievements),
        "unlocked_achievements": len(unlocked),
        "active_challenges": challenges,
    }


@router.get("/challenges")
async def get_challenges(client: Client = Depends(get_current_client)):
    return await crud.gamification.get_active_challenges(client.id)


@router.post("/challenges/evaluate")
async def evaluate_challenges(client: Client = Depends(get_current_client)):
    newly_completed = await crud.gamification.evaluate_challenges(client.id)
    challenges = await crud.gamification.get_active_challenges(client.id)
    return {
        "challenges": challenges,
        "newly_completed": newly_completed,
    }
