from fastapi import FastAPI
from fastapi_cache import FastAPICache

from app.routers import rss
from app.routers import atom
from app.routers import read
from app.settings import settings

app = FastAPI(debug=settings.debug)

app.include_router(rss.router)
app.include_router(atom.router)
app.include_router(read.router)


@app.get("/")
async def root():
    return {"message": "Hello from pocket-bridge !"}


@app.on_event("startup")
async def startup():
    if settings.cache.backend == 'redis':
        print('Using Redis as cache backend.')

        import redis.asyncio as redis
        from redis.asyncio.connection import ConnectionPool
        from fastapi_cache.backends.redis import RedisBackend

        pool = ConnectionPool.from_url(url=settings.cache.redis_url)
        redis = redis.Redis(connection_pool=pool)
        backend = RedisBackend(redis)
    else:
        print('Using in-memory cache backend.')

        from fastapi_cache.backends.inmemory import InMemoryBackend

        backend = InMemoryBackend()
    FastAPICache.init(backend=backend, prefix=settings.cache.prefix)


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app="main:app", host="0.0.0.0", port=8000, reload=True)
