import json
import asyncio
import logging
from typing import Optional, AsyncGenerator
import redis.asyncio as redis
from app.config import settings

logger = logging.getLogger(__name__)

_redis_client: Optional[redis.Redis] = None


async def init_redis():
    global _redis_client
    try:
        _redis_client = redis.from_url(
            settings.REDIS_URL,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
        )
        await _redis_client.ping()
        logger.info("✅ Redis connected")
    except Exception as e:
        logger.warning(f"⚠️  Redis unavailable, notifications disabled: {e}")
        _redis_client = None


async def close_redis():
    global _redis_client
    if _redis_client:
        await _redis_client.close()
        _redis_client = None


async def notify_checkin(user_id: int, status: str, message: str):
    if not _redis_client:
        logger.warning("[REDIS] No Redis client, skipping notify")
        return
    try:
        channel = f"checkin:{user_id}"
        payload = json.dumps({"status": status, "message": message})
        logger.info(f"[REDIS] Publishing to {channel}: {payload}")
        await _redis_client.publish(channel, payload)
    except Exception as e:
        logger.error(f"Redis publish error: {e}")


async def subscribe_checkin(user_id: int) -> AsyncGenerator[dict, None]:
    if not _redis_client:
        logger.warning("[REDIS] No Redis client, subscribe skipped")
        return
    pubsub = _redis_client.pubsub()
    channel = f"checkin:{user_id}"
    logger.info(f"[REDIS] Subscribing to {channel}")
    try:
        await pubsub.subscribe(channel)
        while True:
            message = await asyncio.wait_for(
                pubsub.get_message(ignore_subscribe_messages=True, timeout=30),
                timeout=35,
            )
            if message and message["type"] == "message":
                data = json.loads(message["data"])
                logger.info(f"[REDIS] Received on {channel}: {data}")
                yield data
                break
    except asyncio.TimeoutError:
        pass
    except Exception as e:
        logger.error(f"Redis subscribe error: {e}")
    finally:
        try:
            await pubsub.unsubscribe(channel)
        except Exception:
            pass
        try:
            await pubsub.close()
        except Exception:
            pass
