from typing import List, Optional
from app.models.user import User, UserRoleEnum
from app.utils.auth import hash_password
from tortoise.exceptions import DoesNotExist


async def get_user(user_id: int) -> Optional[User]:
    """Get a specific user by ID"""
    try:
        return await User.get(id=user_id)
    except DoesNotExist:
        return None


async def get_user_by_email(email: str) -> Optional[User]:
    """Get a user by email"""
    try:
        return await User.get(email=email)
    except DoesNotExist:
        return None


async def get_users(skip: int = 0, limit: int = 100) -> List[User]:
    """Get all users with pagination"""
    return await User.all().offset(skip).limit(limit)


async def create_user(user_data: dict) -> User:
    """Create a new user"""
    # Hash the password before storing
    if 'password' in user_data:
        user_data['hashed_password'] = hash_password(user_data.pop('password'))
    return await User.create(**user_data)


async def update_user(user_id: int, user_update: dict) -> Optional[User]:
    """Update a user"""
    user = await get_user(user_id)
    if user:
        for field, value in user_update.items():
            if field == 'password':
                setattr(user, 'hashed_password', hash_password(value))
            else:
                setattr(user, field, value)
        await user.save()
    return user


async def delete_user(user_id: int) -> Optional[User]:
    """Delete a user"""
    user = await get_user(user_id)
    if user:
        await user.delete()
    return user


async def get_users_by_role(role: UserRoleEnum) -> List[User]:
    """Get all users with a specific role"""
    return await User.filter(role=role)


async def get_active_users() -> List[User]:
    """Get all active users"""
    return await User.filter(status=True)