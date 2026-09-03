from typing import List, Optional
from app.models.user import User, UserRoleEnum
from app.utils.auth import hash_password
from tortoise.exceptions import DoesNotExist


async def get_user(user_id: int, tenant_id: Optional[int] = None) -> Optional[User]:
    try:
        filters = {"id": user_id}
        if tenant_id is not None:
            filters["tenant_id"] = tenant_id
        return await User.get(**filters)
    except DoesNotExist:
        return None


async def get_user_by_email(email: str) -> Optional[User]:
    try:
        return await User.get(email=email)
    except DoesNotExist:
        return None


async def get_users(skip: int = 0, limit: int = 100, tenant_id: Optional[int] = None) -> List[User]:
    query = User.all()
    if tenant_id is not None:
        query = query.filter(tenant_id=tenant_id)
    return await query.offset(skip).limit(limit)


async def create_user(user_data: dict, tenant_id: Optional[int] = None) -> User:
    if 'password' in user_data:
        user_data['hashed_password'] = hash_password(user_data.pop('password'))
    if tenant_id is not None and 'tenant_id' not in user_data:
        user_data['tenant_id'] = tenant_id
    return await User.create(**user_data)


async def update_user(user_id: int, user_update, tenant_id: Optional[int] = None) -> Optional[User]:
    user = await get_user(user_id, tenant_id=tenant_id)
    if user:
        if hasattr(user_update, 'model_dump'):
            update_data = user_update.model_dump(exclude_unset=True)
        elif hasattr(user_update, 'dict'):
            update_data = user_update.dict(exclude_unset=True)
        else:
            update_data = user_update

        for field, value in update_data.items():
            if field == 'password':
                setattr(user, 'hashed_password', hash_password(value))
            else:
                setattr(user, field, value)
        await user.save()
    return user


async def delete_user(user_id: int, tenant_id: Optional[int] = None) -> Optional[User]:
    user = await get_user(user_id, tenant_id=tenant_id)
    if user:
        await user.delete()
    return user


async def get_users_by_role(role: UserRoleEnum, tenant_id: Optional[int] = None) -> List[User]:
    filters = {"role": role}
    if tenant_id is not None:
        filters["tenant_id"] = tenant_id
    return await User.filter(**filters)


async def get_active_users(tenant_id: Optional[int] = None) -> List[User]:
    filters = {"status": True}
    if tenant_id is not None:
        filters["tenant_id"] = tenant_id
    return await User.filter(**filters)


async def get_user_by_client_id(client_id: int) -> Optional[User]:
    from app.models.client import Client
    try:
        client = await Client.get(id=client_id)
    except DoesNotExist:
        pass
    return None
