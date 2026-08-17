from typing import List
from app.models.mentor_message import MentorMessage


async def get_client_messages(client_id: int, limit: int = 50) -> List[MentorMessage]:
    return await MentorMessage.filter(client_id=client_id).order_by("-created_at").limit(limit)


async def create_message(client_id: int, role: str, content: str, message_type: str) -> MentorMessage:
    return await MentorMessage.create(
        client_id=client_id,
        role=role,
        content=content,
        message_type=message_type,
    )
