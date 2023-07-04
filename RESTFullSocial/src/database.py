import aioredis
from config import DB_HOST, DB_PASS, DB_USER, DB_NAME, DB_PORT
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from auth.models import Base as auth_base
from auth.models import User
from posts.models import Base as posts_base
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from fastapi_users.db import SQLAlchemyUserDatabase


target_metadata = [auth_base.metadata, posts_base.metadata]
DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

async def get_redis_conn():
    redis = aioredis.from_url("redis://redis:6379")
    async with redis.client() as conn:
        yield conn


engine = create_async_engine(DATABASE_URL)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session

async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)
