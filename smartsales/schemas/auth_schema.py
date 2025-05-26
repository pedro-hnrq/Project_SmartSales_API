from typing import Literal

from pydantic import BaseModel, EmailStr, Field, field_validator

from smartsales.utils.validators import validate_full_name


class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str = Field(min_length=8)
    role: Literal['admin', 'user']

    @field_validator('name')
    def validate_name(cls, v):
        return validate_full_name(v)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenRefreshRequest(BaseModel):
    refresh_token: str = Field(...)


class RegisterResponse(BaseModel):
    name: str
    email: EmailStr
    role: Literal['admin', 'user']


class UserInfo(BaseModel):
    id: int
    email: EmailStr
    role: Literal['admin', 'user']


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: Literal['Bearer'] = 'Bearer'
    exp: int  # UNIX timestamp
    iat: int  # issued at
    user: UserInfo


class RefreshResponse(BaseModel):
    access_token: str
