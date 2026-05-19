from redis.asyncio import Redis
from src.config import Config

URL_CACHE_TTL = 3600

redis_client = Redis(
    host=Config.REDIS_HOST,
    port=Config.REDIS_PORT,
    decode_responses=True
)

async def set_cached_url(short_code:str, original_url: str,):
    key= f"url:{short_code}"

    await redis_client.set(
        name=key,
        value=original_url,
        ex=URL_CACHE_TTL,
    )



async def get_cached_url(short_code: str):
    key = f"url:{short_code}"
    cached_url = await redis_client.get(key)
    return cached_url

async def delete_cached_url(short_code: str):
    key  = f"url:{short_code}"
    await redis_client.delete(key)