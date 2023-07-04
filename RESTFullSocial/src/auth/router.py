import uuid 
from fastapi import APIRouter, Depends
from fastapi_users import FastAPIUsers
from auth.shemas import UserCreate, UserRead, UserUpdate
from auth.dependencies import auth_backend
from auth.user_manager import get_user_manager
from auth.models import User 

auth_router = APIRouter(
        prefix="/auth/jwt", 
        tags=["Auth"]
        )

user_router = APIRouter(
        prefix="/users", 
        tags=["Users"]
        )

fastapi_users = FastAPIUsers[User, uuid.UUID](
        get_user_manager,
        [auth_backend]
        )
current_user = fastapi_users.current_user()


user_router.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
)

auth_router.include_router(
        fastapi_users.get_auth_router(auth_backend), 
        )

auth_router.include_router(
        fastapi_users.get_register_router(UserRead, 
                                          UserCreate), 
        )

auth_router.include_router(
    fastapi_users.get_verify_router(UserRead)
)

auth_router.include_router(
    fastapi_users.get_reset_password_router()
)


@auth_router.get("/test")
async def test_func(user: User = Depends(current_user)):
    return {
            "user": user
            }


