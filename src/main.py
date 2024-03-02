from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from redis.asyncio import Redis

from api import router as api_router
from settings import settings
from db import redis_db
from db.postgres import create_database


@asynccontextmanager
async def lifespan(app: FastAPI):
    from models.users import User  # noqa: F401

    await create_database()
    redis_db.redis = Redis(host=settings.redis.redis_host, port=settings.redis.redis_port)

    yield

    await redis_db.redis.close()


app = FastAPI(
    lifespan=lifespan,
    title=settings.project.project_name,
    docs_url=settings.project.docs_url,
    openapi_url=settings.project.openapi_url,
    version=settings.project.version,
)

app.include_router(api_router, prefix="/api")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",  # noqa: S104
        port=8000,
    )
