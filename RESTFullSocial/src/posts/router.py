from typing import List
from uuid import UUID
from aioredis import Redis
from fastapi import APIRouter, Depends
from auth.router import current_user
from database import get_async_session, get_redis_conn
from posts.dependencies import is_owner_post, is_owner_reaction, reaction_check
from posts.managers import PostManager, ReactionManager
from posts.shemas import  PostModel, ReactionPostModel, UpdatePostModel, ReactionPostForRedisModel
from auth.models import User
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_cache.decorator import cache


router = APIRouter(
        prefix="/post", 
        tags=["Post"]
        )


@router.post('/set_reaction',
            description="Set Reaction.\n is_like = True => like; ",
            dependencies=[Depends(reaction_check)])
async def set_reaction(data: ReactionPostModel,
                       redis: Redis = Depends(get_redis_conn),
                       user: User = Depends(current_user),
                       session: AsyncSession = Depends(get_async_session)) -> ReactionPostModel:

    data.user_id = user.id
    reaction = await ReactionManager.set_reaction(
            data=data, 
            redis=redis,
            session=session
            )
    return reaction

@router.get('/get_reactions')
async def get_reactions(user: User = Depends(current_user), 
                        redis: Redis = Depends(get_redis_conn)) -> List[ReactionPostForRedisModel] | None:
    return await ReactionManager.redis_get(user=user, redis=redis)

@router.delete('/delete_reaction/{id}', 
               dependencies=[Depends(is_owner_reaction)])
async def delete_reaction(id: UUID,
                          redis: Redis = Depends(get_redis_conn),
                          user: User = Depends(current_user), 
                          session: AsyncSession = Depends(get_async_session)) -> None:
    await ReactionManager.redis_delete(id=id, user=user, redis=redis) 

    return await ReactionManager.delete_reaction(id=id, session=session)


@router.post('/create_post')
async def create_post(data:PostModel, 
                      user: User = Depends(current_user),
                      session: AsyncSession = Depends(get_async_session)) -> PostModel:
    data.user_id = user.id
    await PostManager.create_post(data=data, session=session) 
    return data

@router.get('/get_post_by_id/{id}')
async def get_post_by_id(id: UUID, 
                         session: AsyncSession = Depends(get_async_session)):
    return await PostManager.get_post_by_id(
            id=id, 
            session=session
            )

@router.get("/get_post_by_user")
async def get_post_by_user(user: User = Depends(current_user), 
                           session: AsyncSession = Depends(get_async_session)) -> List[PostModel]:
    return await PostManager.get_user_post(
            user_id=user.id, 
            session=session
            )


@router.put('/update_post/{post_id}', 
            dependencies=[Depends(is_owner_post)])
async def update_post(post_id: UUID, 
                      data: UpdatePostModel, 
                      session: AsyncSession = Depends(get_async_session)) -> None:
    return await PostManager.update_post(
            post_id=post_id, 
            data=data, 
            session=session
            )

@router.delete("/delete_post", 
               dependencies=[Depends(is_owner_post)])
async def delete_post(post_id: UUID, 
                      session: AsyncSession = Depends(get_async_session)) -> None:
    await PostManager.delete_post(
            post_id=post_id, 
            session=session
            )

@router.get("/view_posts")
@cache(expire=60)
async def view_posts(session: AsyncSession = Depends(get_async_session)):
    return await PostManager.view_all_posts(
            limit=0, 
            offset=20, 
            session=session
            )

