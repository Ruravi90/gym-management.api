from typing import List, Optional
from app.models.gym_class import GymClass
from tortoise.exceptions import DoesNotExist
from datetime import datetime, timezone


async def get_gym_class(class_id: int, tenant_id: Optional[int] = None) -> Optional[GymClass]:
    """Get a specific gym class by ID"""
    try:
        filters = {"id": class_id}
        if tenant_id is not None:
            filters["tenant_id"] = tenant_id
        return await GymClass.get(**filters)
    except DoesNotExist:
        return None


async def get_gym_classes(skip: int = 0, limit: int = 100, tenant_id: Optional[int] = None) -> List[GymClass]:
    """Get all gym classes with pagination"""
    query = GymClass.all()
    if tenant_id is not None:
        query = query.filter(tenant_id=tenant_id)
    return await query.offset(skip).limit(limit)


async def get_upcoming_classes(skip: int = 0, limit: int = 100, tenant_id: Optional[int] = None) -> List[GymClass]:
    """Get upcoming scheduled classes"""
    filters = {
        "status": "scheduled",
        "start_time__gte": datetime.now(timezone.utc),
    }
    if tenant_id is not None:
        filters["tenant_id"] = tenant_id
    return await GymClass.filter(**filters).order_by("start_time").offset(skip).limit(limit)


async def create_gym_class(class_data: dict, tenant_id: Optional[int] = None) -> GymClass:
    """Create a new gym class"""
    if tenant_id is not None:
        class_data["tenant_id"] = tenant_id
    return await GymClass.create(**class_data)


async def update_gym_class(class_id: int, class_update: dict, tenant_id: Optional[int] = None) -> Optional[GymClass]:
    """Update a gym class"""
    gym_class = await get_gym_class(class_id, tenant_id=tenant_id)
    if gym_class:
        for field, value in class_update.items():
            setattr(gym_class, field, value)
        await gym_class.save()
    return gym_class


async def delete_gym_class(class_id: int, tenant_id: Optional[int] = None) -> Optional[GymClass]:
    """Delete a gym class"""
    gym_class = await get_gym_class(class_id, tenant_id=tenant_id)
    if gym_class:
        await gym_class.delete()
    return gym_class


async def get_classes_by_instructor(instructor: str, tenant_id: Optional[int] = None) -> List[GymClass]:
    """Get all classes by a specific instructor"""
    filters = {"instructor": instructor}
    if tenant_id is not None:
        filters["tenant_id"] = tenant_id
    return await GymClass.filter(**filters)


async def get_classes_by_status(status: str, tenant_id: Optional[int] = None) -> List[GymClass]:
    """Get all classes with a specific status"""
    filters = {"status": status}
    if tenant_id is not None:
        filters["tenant_id"] = tenant_id
    return await GymClass.filter(**filters)
