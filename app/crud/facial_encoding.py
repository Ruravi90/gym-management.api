from typing import Optional
from ..models.facial_encoding import FacialEncoding

async def get_facial_encoding_by_client(client_id: int) -> Optional[FacialEncoding]:
    """Get facial encoding for a specific client"""
    return await FacialEncoding.filter(client_id=client_id).first()

async def create_facial_encoding(client_id: int, encoding_data: bytes) -> FacialEncoding:
    """Create a new facial encoding"""
    return await FacialEncoding.create(
        client_id=client_id,
        encoding_data=encoding_data
    )

async def update_facial_encoding(client_id: int, encoding_data: bytes) -> Optional[FacialEncoding]:
    """Update facial encoding for a client"""
    db_facial_encoding = await get_facial_encoding_by_client(client_id)
    if db_facial_encoding:
        db_facial_encoding.encoding_data = encoding_data
        await db_facial_encoding.save()
        return db_facial_encoding
    return None

async def delete_facial_encoding(client_id: int) -> bool:
    """Delete facial encoding for a client"""
    count = await FacialEncoding.filter(client_id=client_id).delete()
    return count > 0