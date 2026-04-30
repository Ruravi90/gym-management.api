from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List
from app import crud, schemas
from app.utils.auth import get_current_user
from app.models.user import User as UserModel
from app.models.client import Client

router = APIRouter()

async def get_current_client(current_user: UserModel = Depends(get_current_user)):
    client = await Client.get_or_none(user_id=current_user.id)
    if not client:
        # Auto-create client profile for users who don't have one
        client = await Client.create(
            name=current_user.name,
            email=current_user.email,
            phone=current_user.phone,
            user_id=current_user.id
        )
    return client

@router.get("/habits", response_model=List[schemas.kaizen.HabitResponse])
async def get_habits(
    month: int = Query(..., description="Month (1-12)"),
    year: int = Query(..., description="Year"),
    client: Client = Depends(get_current_client)
):
    """Get all Kaizen habits for the current user for a specific month and year"""
    return await crud.kaizen.get_habits(client_id=client.id, month=month, year=year)

@router.post("/habits", response_model=schemas.kaizen.HabitResponse)
async def create_habit(habit: schemas.kaizen.HabitCreate, client: Client = Depends(get_current_client)):
    """Create a new Kaizen habit"""
    return await crud.kaizen.create_habit(client_id=client.id, habit_data=habit)

@router.put("/habits/{habit_id}", response_model=schemas.kaizen.HabitResponse)
async def update_habit(habit_id: int, habit: schemas.kaizen.HabitUpdate, client: Client = Depends(get_current_client)):
    """Update an existing habit (reflection, goal, etc)"""
    db_habit = await crud.kaizen.get_habit(habit_id=habit_id)
    if not db_habit or db_habit.client_id != client.id:
        raise HTTPException(status_code=404, detail="Habit not found")
    return await crud.kaizen.update_habit(habit_id=habit_id, habit_data=habit)

@router.delete("/habits/{habit_id}", status_code=204)
async def delete_habit(habit_id: int, client: Client = Depends(get_current_client)):
    """Delete an existing habit"""
    db_habit = await crud.kaizen.get_habit(habit_id=habit_id)
    if not db_habit or db_habit.client_id != client.id:
        raise HTTPException(status_code=404, detail="Habit not found")
    await crud.kaizen.delete_habit(habit_id=habit_id)
    return None

@router.post("/habits/{habit_id}/logs", response_model=schemas.kaizen.KaizenLogResponse)
async def record_habit_log(habit_id: int, log_data: schemas.kaizen.KaizenLogCreate, client: Client = Depends(get_current_client)):
    """Record a daily victory or defeat for a habit"""
    db_habit = await crud.kaizen.get_habit(habit_id=habit_id)
    if not db_habit or db_habit.client_id != client.id:
        raise HTTPException(status_code=404, detail="Habit not found")
        
    # Bottleneck progression check
    if log_data.status == "victory":
        all_habits = await crud.kaizen.get_habits(client_id=client.id, month=db_habit.month, year=db_habit.year)
        if len(all_habits) > 1:
            vics = [sum(1 for l in h.logs if l.status == "victory") for h in all_habits]
            min_vics = min(vics)
            current_vics = sum(1 for l in db_habit.logs if l.status == "victory")
            if (current_vics - min_vics) >= 3:
                raise HTTPException(status_code=400, detail="Debes emparejar tus hábitos más olvidados antes de seguir avanzando en este.")
    
    log = await crud.kaizen.record_log(habit_id=habit_id, log_data=log_data)
    
    # Evaluate and award medals based on new logs
    await crud.kaizen.check_and_award_medals(client_id=client.id, habit_id=habit_id)
    # Revoke medals if penalizations apply
    await crud.kaizen.check_penalizations(client_id=client.id)
    
    return log

@router.get("/medals", response_model=List[schemas.kaizen.MedalResponse])
async def get_medals(client: Client = Depends(get_current_client)):
    """Get all medals earned by the current user"""
    return await crud.kaizen.get_medals(client_id=client.id)

# TODO: Background task or specific endpoint to evaluate and award medals
