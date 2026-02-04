from typing import Optional
from fastapi_users import schemas
from pydantic import EmailStr, field_validator
from beanie import PydanticObjectId


class UserRead(schemas.BaseUser[str]):
    """Schema for reading user data"""
    id: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_verified: bool = True

    @field_validator('id', mode='before')
    @classmethod
    def convert_objectid_to_str(cls, v):
        if isinstance(v, PydanticObjectId):
            return str(v)
        return v


class UserCreate(schemas.BaseUserCreate):
    """Schema for creating a new user"""
    email: EmailStr
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_verified: Optional[bool] = True


class UserUpdate(schemas.BaseUserUpdate):
    """Schema for updating user data"""
    password: Optional[str] = None
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_verified: Optional[bool] = None
