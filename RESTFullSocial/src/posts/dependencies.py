from uuid import UUID
from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from auth.models import User
from auth.router import current_user
from database import get_async_session
from posts.models import Post, ReactionPost
from posts.shemas import ReactionPostModel


async def __check_owner_post(post_id: UUID, 
                           user: User, 
                           session: AsyncSession) -> bool:
    query = select(Post).where(
            Post.user_id == user.id, 
            Post.id == post_id
            )
    res = await session.execute(query)
    if res.scalar():
        return True
    return False



async def is_owner_post(
        post_id: UUID,
        user: User = Depends(current_user), 
        session: AsyncSession = Depends(get_async_session)
        ) -> None:
    if not await __check_owner_post(post_id, user, session):
        raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND
                )

async def is_owner_reaction(id: UUID, 
                            user: User = Depends(current_user), 
                            session: AsyncSession = Depends(get_async_session)) -> None:
    query = select(ReactionPost).where(
            ReactionPost.id == id, 
            ReactionPost.user_id == user.id
            )
    res = await session.execute(query)
    if not res.scalar():
        raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND
                )

async def reaction_check(
        data: ReactionPostModel, 
        user: User = Depends(current_user),
        session: AsyncSession = Depends(get_async_session)
        ) -> None:
    if await __check_owner_post(data.post_id, user, session):
        raise HTTPException(
                status_code=status.HTTP_410_GONE, 
                detail="Operation not possible"
                )
    query = select(Post).where(Post.id == data.post_id)
    res = await session.execute(query)
    if not res.scalar(): 
        raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Post not found"
                )
    

