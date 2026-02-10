from typing import List, Optional
from app.models.client import Client
from tortoise.exceptions import DoesNotExist


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


async def create_client(client_data: dict) -> Client:
    """Create a new client"""
    return await Client.create(**client_data)


async def update_client(client_id: int, client_update: dict) -> Optional[Client]:
    """Update a client"""
    client = await get_client(client_id)
    if client:
        for field, value in client_update.items():
            setattr(client, field, value)
        await client.save()
    return client


async def delete_client(client_id: int) -> Optional[Client]:
    """Delete a client"""
    client = await get_client(client_id)
    if client:
        await client.delete()
    return client


async def get_clients_by_membership_type(membership_type: str) -> List[Client]:
    """Get all clients with a specific membership type"""
    return await Client.filter(membership_type=membership_type)


async def get_active_clients() -> List[Client]:
    """Get all active clients"""
    return await Client.filter(status=True)