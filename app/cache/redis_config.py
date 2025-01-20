import redis
import os
import json
from typing import Optional, Any
from dotenv import load_dotenv

load_dotenv()

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
CACHE_TTL = int(os.getenv("CACHE_TTL", "3600"))

redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    decode_responses=True
)

def set_cache(key: str, value: Any, ttl: int = CACHE_TTL) -> None:
    """Store value in cache"""
    try:
        redis_client.setex(key, ttl, json.dumps(value))
    except Exception:
        pass

def get_cache(key: str) -> Optional[Any]:
    """Retrieve value from cache"""
    try:
        data = redis_client.get(key)
        return json.loads(data) if data else None
    except Exception:
        return None

def delete_cache(key: str) -> None:
    """Delete value from cache"""
    try:
        redis_client.delete(key)
    except Exception:
        pass

def clear_cache() -> None:
    """Clear all cache"""
    try:
        redis_client.flushall()
    except Exception:
        pass 