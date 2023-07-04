from collections.abc import AsyncGenerator
import uuid
from typing import Optional
from fastapi import Depends, Request
from fastapi_users import BaseUserManager, UUIDIDMixin
from auth.models import User
from config import RESET_SECRET, VERIFICATION_SECRET
from database import get_user_db



class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = RESET_SECRET
    verification_token_secret = VERIFICATION_SECRET

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        ...

    async def on_after_forgot_password(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        ...

    async def on_after_request_verify(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        ...


async def get_user_manager(user_db=Depends(get_user_db)) -> AsyncGenerator:
    yield UserManager(user_db)
