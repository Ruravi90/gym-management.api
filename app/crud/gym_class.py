from typing import List, Optional
from app.models.gym_class import GymClass
from tortoise.exceptions import DoesNotExist
from datetime import datetime, timezone


async def get_gym_class(class_id: int) -> Optional[GymClass]:
    """Get a specific gym class by ID"""
    try:
        return await GymClass.get(id=class_id)
    except DoesNotExist:
        return None


async def get_gym_classes(skip: int = 0, limit: int = 100) -> List[GymClass]:
    """Get all gym classes with pagination"""
    return await GymClass.all().offset(skip).limit(limit)


async def get_upcoming_classes(skip: int = 0, limit: int = 100) -> List[GymClass]:
    """Get upcoming scheduled classes"""
    return await GymClass.filter(
        status="scheduled",
        start_time__gte=datetime.now(timezone.utc)
    ).order_by("start_time").offset(skip).limit(limit)


async def create_gym_class(class_data: dict) -> GymClass:
    """Create a new gym class"""
    return await GymClass.create(**class_data)


async def update_gym_class(class_id: int, class_update: dict) -> Optional[GymClass]:
    """Update a gym class"""
    gym_class = await get_gym_class(class_id)
    if gym_class:
        for field, value in class_update.items():
            setattr(gym_class, field, value)
        await gym_class.save()
    return gym_class


async def delete_gym_class(class_id: int) -> Optional[GymClass]:
    """Delete a gym class"""
    gym_class = await get_gym_class(class_id)
    if gym_class:
        await gym_class.delete()
    return gym_class


async def get_classes_by_instructor(instructor: str) -> List[GymClass]:
    """Get all classes by a specific instructor"""
    return await GymClass.filter(instructor=instructor)


async def get_classes_by_status(status: str) -> List[GymClass]:
    """Get all classes with a specific status"""
    return await GymClass.filter(status=status)
