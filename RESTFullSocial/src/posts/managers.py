import json
from uuid import UUID, uuid4
from aioredis import Redis
from fastapi import HTTPException, status
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from posts.shemas import AllPostModel, PostModel, ReactionPostForRedisModel, UpdatePostModel, ReactionPostModel
from posts.models import Post, ReactionPost
from auth.models import User
from typing import Any, List



class PostManager:

    @staticmethod
    async def create_post(data: PostModel, 
                          session: AsyncSession) -> None:
        post = Post(**data.dict())
        session.add(post)
        await session.commit()

    @staticmethod
    async def get_post_by_id(id: UUID,
                             session: AsyncSession):
        query = select(Post).where(Post.id == id)
        res = await session.execute(query)
        res = res.scalar()
        if not res:
            raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND
                    )
        return PostModel.from_orm(res)
        

    @staticmethod
    async def get_user_post(user_id: UUID, 
                            session: AsyncSession) -> List[PostModel]:
        query = select(Post).where(
                Post.user_id == user_id 
                )
        res = await session.execute(query)
        res = res.scalars()
        
        if not res: 
            raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND
                    )
        res = [PostModel.from_orm(post) for post in res ]
        return res
    

    @staticmethod
    async def update_post(post_id: UUID, 
                          data: UpdatePostModel, 
                          session: AsyncSession) -> None:
        query = (update(Post)
                .where(Post.id == post_id)
                .values(**data.dict()))
        res = await session.execute(query) 
        if not res: raise HTTPException(status_code=status.HTTP_404_NOT_FOUND) 
        await session.commit()

    @staticmethod
    async def delete_post(post_id: UUID, 
                          session: AsyncSession) -> None:
        query = delete(Post).where(Post.id == post_id)
        await session.execute(query)
        await session.commit()


    @staticmethod
    async def view_all_posts(limit: int, offset: int, 
                             session: AsyncSession):
        query = select(Post.id, Post.title, Post.body, Post.created_at, User.email)\
                .join(User, Post.user_id == User.id)\
                .order_by(Post.created_at.desc())
        res = await session.execute(query)
        res = res.mappings().all()
        return [AllPostModel.from_orm(post) for post in res]
        

class ReactionManager:

    @staticmethod
    async def __collect_data_for_redis_reaction(
            data: ReactionPostModel, 
            session: AsyncSession) -> ReactionPostForRedisModel:

        query = select(Post.title, Post.body, User.email)\
                .join(User, Post.user_id == User.id) \
                .where(Post.id == data.post_id)

        res = await session.execute(query)
        res = res.mappings().all()
        result = ReactionPostForRedisModel(
                id=data.id, 
                post_id=data.post_id, 
                is_like=data.is_like, 
                title=res[0]["title"], 
                body=res[0]["body"], 
                author=res[0]["email"]
                )
        return result

    @staticmethod 
    async def redis_set(
            user_id: UUID,  
            data: ReactionPostForRedisModel,
            redis: Redis) -> None:
        is_data = await redis.get(str(user_id))
        if is_data is None: 
            await redis.set(
                    str(user_id), 
                    json.dumps([data.json()])
                    )
        else:
            is_data = json.loads(is_data)
            is_data = [reaction 
                       for reaction in is_data 
                       if json.loads(reaction)["id"] != str(data.id)
                       ]
            is_data.append(data.json())
            await redis.set(
                    str(user_id), 
                    json.dumps(is_data)
                    )

    @staticmethod
    async def redis_get(user: User, redis: Redis) -> List[ReactionPostForRedisModel] | None:
        data = await redis.get(str(user.id)) 
        if data is None: return None

        data = json.loads(data)

        return [ReactionPostForRedisModel(**json.loads(reaction))
                for reaction in data 
                if reaction is not None]

    @staticmethod
    async def redis_delete(user: User, id: UUID, redis: Redis) -> None:
        data = await redis.get(str(user.id))
        data = json.loads(data)
        data =  [json.loads(reaction) 
                 for reaction in data 
                 if json.loads(reaction)["id"] != str(id) ]

        data = [json.dumps(reaction) for reaction in data]
        await redis.set(str(user.id), json.dumps(data))

    @classmethod
    async def set_reaction(cls, data: ReactionPostModel, 
                           session: AsyncSession, 
                           redis: Redis) -> Any:
        query = select(ReactionPost).where(
                ReactionPost.post_id == data.post_id, 
                ReactionPost.user_id == data.user_id
                )
        res = await session.execute(query)
        res = res.scalar()
        if res and res.is_like == data.is_like: data.id = res.id
        elif res and res.is_like != data.is_like:
            query = update(ReactionPost)\
                    .where(ReactionPost.id == res.id)\
                    .values(is_like=data.is_like)
            await session.execute(query)
            await session.commit()
            data.id = res.id
        else:
            reaction = ReactionPost(
                    **data.dict()
                    )
            session.add(reaction)
            await session.commit()
        redis_data = await cls.__collect_data_for_redis_reaction(
                data=data, 
                session=session
                )

        await cls.redis_set(user_id=data.user_id, 
                            data=redis_data, 
                            redis=redis
                            )
        return data

    @staticmethod
    async def delete_reaction(id: UUID, 
                              session: AsyncSession) -> None:
        query = delete(ReactionPost).where(ReactionPost.id == id)
        await session.execute(query)
        await session.commit()









