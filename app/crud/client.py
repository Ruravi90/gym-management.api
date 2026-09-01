from typing import List, Optional
from app.models.client import Client
from tortoise.exceptions import DoesNotExist
from tortoise.expressions import Q
from app.services.audit_service import AuditService
from app.models.audit_log import ActionTypeEnum


async def get_client(client_id: int, tenant_id: Optional[int] = None) -> Optional[Client]:
    try:
        filters = {"id": client_id}
        if tenant_id is not None:
            filters["tenant_id"] = tenant_id
        return await Client.get(**filters).prefetch_related("user")
    except DoesNotExist:
        return None


async def get_client_by_email(email: str, tenant_id: Optional[int] = None) -> Optional[Client]:
    try:
        filters = {"email": email}
        if tenant_id is not None:
            filters["tenant_id"] = tenant_id
        return await Client.get(**filters)
    except DoesNotExist:
        return None


async def get_client_by_phone(phone: str, tenant_id: Optional[int] = None) -> Optional[Client]:
    try:
        filters = {"phone": phone}
        if tenant_id is not None:
            filters["tenant_id"] = tenant_id
        return await Client.get(**filters)
    except DoesNotExist:
        return None


async def get_client_by_user_id(user_id: int) -> Optional[Client]:
    try:
        return await Client.get(user_id=user_id)
    except DoesNotExist:
        return None


async def get_clients(skip: int = 0, limit: int = 100, tenant_id: Optional[int] = None) -> List[Client]:
    query = Client.all()
    if tenant_id is not None:
        query = query.filter(tenant_id=tenant_id)
    return await query.prefetch_related("user").offset(skip).limit(limit)


async def create_client(
    client_data: dict,
    user_id: Optional[int] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    tenant_id: Optional[int] = None,
) -> Client:
    db_user_id = client_data.pop("user_id", None)
    if tenant_id is not None:
        client_data["tenant_id"] = tenant_id
    client = await Client.create(**client_data, user_id=db_user_id)

    await AuditService.log_creation(
        user_id=user_id,
        entity_type="Client",
        entity_id=client.id,
        new_values=await AuditService.extract_entity_values_for_audit(client),
        ip_address=ip_address,
        user_agent=user_agent,
        tenant_id=tenant_id,
    )

    return client


async def update_client(
    client_id: int,
    client_update: dict,
    user_id: Optional[int] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    tenant_id: Optional[int] = None,
) -> Optional[Client]:
    client = await get_client(client_id, tenant_id=tenant_id)
    if client:
        old_values = await AuditService.extract_entity_values_for_audit(client)

        for field, value in client_update.items():
            setattr(client, field, value)
        await client.save()

        new_values = await AuditService.extract_entity_values_for_audit(client)

        await AuditService.log_update(
            user_id=user_id,
            entity_type="Client",
            entity_id=client.id,
            old_values=old_values,
            new_values=new_values,
            ip_address=ip_address,
            user_agent=user_agent,
            tenant_id=tenant_id,
        )

    return client


async def delete_client(
    client_id: int,
    user_id: Optional[int] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    tenant_id: Optional[int] = None,
) -> Optional[Client]:
    client = await get_client(client_id, tenant_id=tenant_id)
    if client:
        old_values = await AuditService.extract_entity_values_for_audit(client)

        await client.delete()

        await AuditService.log_deletion(
            user_id=user_id,
            entity_type="Client",
            entity_id=client.id,
            old_values=old_values,
            ip_address=ip_address,
            user_agent=user_agent,
            tenant_id=tenant_id,
        )
    return client


async def get_clients_by_membership_type(membership_type: str, tenant_id: Optional[int] = None) -> List[Client]:
    filters = {"membership_type": membership_type}
    if tenant_id is not None:
        filters["tenant_id"] = tenant_id
    return await Client.filter(**filters)


async def get_active_clients(tenant_id: Optional[int] = None) -> List[Client]:
    filters = {"status": True}
    if tenant_id is not None:
        filters["tenant_id"] = tenant_id
    return await Client.filter(**filters)


async def search_clients(
    search_term: str,
    skip: int = 0,
    limit: int = 100,
    tenant_id: Optional[int] = None,
) -> List[Client]:
    q = Q(name__icontains=search_term) | Q(email__icontains=search_term) | Q(phone__icontains=search_term)
    query = Client.filter(q)
    if tenant_id is not None:
        query = query.filter(tenant_id=tenant_id)
    return await query.offset(skip).limit(limit)
