from typing import List, Optional
from app.models.client import Client
from tortoise.exceptions import DoesNotExist
from app.services.audit_service import AuditService
from app.models.audit_log import ActionTypeEnum


async def get_client(client_id: int) -> Optional[Client]:
    """Get a specific client by ID"""
    try:
        return await Client.get(id=client_id)
    except DoesNotExist:
        return None


async def get_client_by_email(email: str) -> Optional[Client]:
    """Get a client by email"""
    try:
        return await Client.get(email=email)
    except DoesNotExist:
        return None


async def get_clients(skip: int = 0, limit: int = 100) -> List[Client]:
    """Get all clients with pagination"""
    return await Client.all().offset(skip).limit(limit)


async def create_client(client_data: dict, user_id: Optional[int] = None, ip_address: Optional[str] = None, user_agent: Optional[str] = None) -> Client:
    """Create a new client"""
    # Extract user_id if provided in client_data
    db_user_id = client_data.pop("user_id", None)
    client = await Client.create(**client_data, user_id=db_user_id)

    # Log the creation in the audit log
    await AuditService.log_creation(
        user_id=user_id,
        entity_type="Client",
        entity_id=client.id,
        new_values=await AuditService.extract_entity_values_for_audit(client),
        ip_address=ip_address,
        user_agent=user_agent
    )

    return client


async def update_client(
    client_id: int,
    client_update: dict,
    user_id: Optional[int] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None
) -> Optional[Client]:
    """Update a client"""
    client = await get_client(client_id)
    if client:
        # Get the old values before updating
        old_values = await AuditService.extract_entity_values_for_audit(client)

        # Update the client
        for field, value in client_update.items():
            setattr(client, field, value)
        await client.save()

        # Get the new values after updating
        new_values = await AuditService.extract_entity_values_for_audit(client)

        # Log the update in the audit log
        await AuditService.log_update(
            user_id=user_id,
            entity_type="Client",
            entity_id=client.id,
            old_values=old_values,
            new_values=new_values,
            ip_address=ip_address,
            user_agent=user_agent
        )

    return client


async def delete_client(
    client_id: int,
    user_id: Optional[int] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None
) -> Optional[Client]:
    """Delete a client"""
    client = await get_client(client_id)
    if client:
        # Get the old values before deleting
        old_values = await AuditService.extract_entity_values_for_audit(client)

        await client.delete()

        # Log the deletion in the audit log
        await AuditService.log_deletion(
            user_id=user_id,
            entity_type="Client",
            entity_id=client.id,
            old_values=old_values,
            ip_address=ip_address,
            user_agent=user_agent
        )
    return client


async def get_clients_by_membership_type(membership_type: str) -> List[Client]:
    """Get all clients with a specific membership type"""
    return await Client.filter(membership_type=membership_type)


async def get_active_clients() -> List[Client]:
    """Get all active clients"""
    return await Client.filter(status=True)


async def search_clients(search_term: str, skip: int = 0, limit: int = 100) -> List[Client]:
    """Search clients by name, email, or phone"""
    from tortoise.expressions import Q
    return await Client.filter(
        Q(name__icontains=search_term) |
        Q(email__icontains=search_term) |
        Q(phone__icontains=search_term)
    ).offset(skip).limit(limit)