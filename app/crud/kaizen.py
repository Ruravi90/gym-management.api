from typing import List, Optional
from datetime import date
from fastapi import HTTPException, status
from app.models.kaizen import KaizenHabit, KaizenLog, KaizenMedal, KaizenLogStatus, MedalType
from app.models.client import Client
from app.schemas.kaizen import HabitCreate, HabitUpdate, KaizenLogCreate

async def get_habits(client_id: int, month: int, year: int) -> List[KaizenHabit]:
    return await KaizenHabit.filter(client_id=client_id, month=month, year=year).prefetch_related("logs")

async def get_habit(habit_id: int) -> Optional[KaizenHabit]:
    return await KaizenHabit.get_or_none(id=habit_id).prefetch_related("logs")

async def create_habit(client_id: int, habit_data: HabitCreate) -> KaizenHabit:
    habit = await KaizenHabit.create(
        client_id=client_id,
        **habit_data.model_dump()
    )
    await habit.fetch_related("logs")
    return habit

async def update_habit(habit_id: int, habit_data: HabitUpdate) -> Optional[KaizenHabit]:
    habit = await KaizenHabit.get_or_none(id=habit_id)
    if not habit:
        return None
    
    update_data = habit_data.model_dump(exclude_unset=True)
    if update_data:
        await habit.update_from_dict(update_data)
        await habit.save()
    return await get_habit(habit_id)

async def delete_habit(habit_id: int) -> bool:
    habit = await KaizenHabit.get_or_none(id=habit_id)
    if not habit:
        return False
    await habit.delete()
    return True

async def record_log(habit_id: int, log_data: KaizenLogCreate) -> KaizenLog:
    # Use update_or_create to handle both inserting a new log or updating an existing one for the same date
    log, created = await KaizenLog.update_or_create(
        habit_id=habit_id, date=log_data.date,
        defaults={"status": log_data.status, "reflection": log_data.reflection}
    )
    return log

async def get_medals(client_id: int) -> List[KaizenMedal]:
    return await KaizenMedal.filter(client_id=client_id)

async def award_medal(client_id: int, type: MedalType, description: str) -> KaizenMedal:
    # Evita duplicados si el cliente ya tiene esa medalla
    existing = await KaizenMedal.get_or_none(client_id=client_id, type=type)
    if existing:
        return existing
        
    return await KaizenMedal.create(
        client_id=client_id,
        type=type,
        description=description,
        earned_date=date.today()
    )

async def check_and_award_medals(client_id: int, habit_id: int):
    """
    Evaluates medal logic after a new log is recorded.
    """
    # Obtenemos todos los logs de este hábito ordenados por fecha
    logs = await KaizenLog.filter(habit_id=habit_id, status="victory").order_by("date")
    total_victories = len(logs)
    
    if total_victories == 0:
        return

    # Bronce (Diaria): Primera victoria
    if total_victories >= 1:
        await award_medal(client_id, "daily", "Has logrado tu primera victoria diaria.")
        
    # Oro (Mensual): 25 victorias en el mismo mes (para simplificar, comprobaremos si hay 25 victorias globales en este hábito)
    # Una implementación más estricta agruparía por month(date), pero global por hábito fomenta el uso a largo plazo.
    if total_victories >= 25:
        await award_medal(client_id, "monthly", "¡Increíble! Lograste 25 victorias en este hábito.")
        
    # Corona (Anual): 300 victorias
    if total_victories >= 300:
        await award_medal(client_id, "yearly", "Leyenda: Has superado las 300 victorias en tu hábito.")

    # Plata (Semanal): 7 días consecutivos
    if total_victories >= 7:
        streak = 1
        max_streak = 1
        from datetime import datetime
        
        for i in range(1, len(logs)):
            # Convertimos a formato de fecha si son strings
            date_prev = datetime.strptime(logs[i-1].date, "%Y-%m-%d").date() if isinstance(logs[i-1].date, str) else logs[i-1].date
            date_curr = datetime.strptime(logs[i].date, "%Y-%m-%d").date() if isinstance(logs[i].date, str) else logs[i].date
            
            delta = (date_curr - date_prev).days
            if delta == 1:
                streak += 1
                if streak > max_streak:
                    max_streak = streak
            elif delta > 1:
                streak = 1
                
        if max_streak >= 7:
            await award_medal(client_id, "weekly", "Has logrado una racha invicta de 7 días consecutivos.")

async def check_penalizations(client_id: int):
    """
    Evaluates if any medals should be revoked based on strict rules.
    """
    from datetime import datetime
    
    # Evaluar pérdida de Bronce: 3 derrotas consecutivas en cualquier hábito
    # Evaluar pérdida de Plata: Si hubo alguna derrota hoy
    # Evaluar pérdida de Oro: Porcentaje de éxito mensual global < 50%
    
    habits = await KaizenHabit.filter(client_id=client_id).prefetch_related("logs")
    
    revoke_bronze = False
    revoke_silver = False
    total_logs = 0
    total_vics = 0
    
    for h in habits:
        logs = sorted(h.logs, key=lambda x: x.date)
        if len(logs) >= 3:
            last_3 = logs[-3:]
            if all(l.status == "defeat" for l in last_3):
                revoke_bronze = True
                
        if len(logs) > 0:
            if logs[-1].status == "defeat":
                revoke_silver = True
                
        total_logs += len(logs)
        total_vics += sum(1 for l in logs if l.status == "victory")
        
    if revoke_bronze:
        await KaizenMedal.filter(client_id=client_id, type="daily").delete()
        
    if revoke_silver:
        await KaizenMedal.filter(client_id=client_id, type="weekly").delete()
        
    if total_logs > 10 and (total_vics / total_logs) < 0.5:
        await KaizenMedal.filter(client_id=client_id, type="monthly").delete()
