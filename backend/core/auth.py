from fastapi_users import FastAPIUsers
from fastapi_users.authentication import AuthenticationBackend, BearerTransport, JWTStrategy
from fastapi_users.manager import BaseUserManager
from fastapi_users.db import BeanieBaseUser, BeanieUserDatabase
from fastapi import Depends, Request
from typing import Optional
from beanie import PydanticObjectId, Document, Indexed
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pydantic import EmailStr
from .config import settings



class User(BeanieBaseUser, Document):
    """User model for authentication"""
    email: Indexed(EmailStr, unique=True)
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_verified: bool = True  # Default to verified
    
    class Settings:
        name = "users"
        email_collation = None


async def get_user_db():
    """Get user database instance"""
    yield BeanieUserDatabase(User)

# Basic User Manager class
# TODO Add user email verification, password reset email sending, ...
class UserManager(BaseUserManager[User, PydanticObjectId]):
    reset_password_token_secret = settings.secret_key
    verification_token_secret = settings.secret_key

    def parse_id(self, value) -> PydanticObjectId:
        """Parse string ID to PydanticObjectId"""
        if isinstance(value, PydanticObjectId):
            return value
        return PydanticObjectId(value)
    
    async def on_after_register(self, user: User, request: Optional[Request] = None):
        print(f"New User registered - ID: {user.id}, Name: {user.first_name}, Email: {user.email}")


async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)


# JWT Strategy
def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=settings.secret_key, lifetime_seconds=3600)

# JWT Stateless Authentication Backend
# (No server side session)
auth_backend = AuthenticationBackend(
    name="jwt",
    transport=BearerTransport(tokenUrl="auth/jwt/login"),
    get_strategy=get_jwt_strategy,
)

# FastAPI Users instance
fastapi_users = FastAPIUsers[User, PydanticObjectId](get_user_manager, [auth_backend])

# Current active user definitions
current_active_user = fastapi_users.current_user(active=True)
current_superuser = fastapi_users.current_user(active=True, superuser=True)
