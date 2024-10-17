from redis.asyncio import (
    from_url,
    Redis,
)


def init_redis_pool(host: str, port: str) -> Redis:
    session = from_url(
        f"redis://{host}:{port}/0", encoding="utf-8", decode_responses=True,
    )
    yield session
    session.close()
    session.wait_closed()
