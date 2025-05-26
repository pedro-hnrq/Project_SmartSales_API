from http import HTTPStatus
from time import time

from fastapi import HTTPException
from jwt import DecodeError, ExpiredSignatureError, decode
from sqlalchemy.orm import Session

from smartsales.core.security import (
    create_access_token,
    create_refresh_token,
    get_password_hash,
    verify_password,
)
from smartsales.core.settings import Settings
from smartsales.models.auth import Auth, UserRole
from smartsales.schemas.auth_schema import LoginRequest, RegisterRequest

settings = Settings()


def register_user(data: RegisterRequest, db: Session) -> Auth:
    user = db.query(Auth).filter(Auth.email == data.email).first()
    if user:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT, detail='Email already registered'
        )
    hashed = get_password_hash(data.password)
    new_user = Auth(
        name=data.name,
        email=data.email,
        password=hashed,
        role=UserRole(data.role),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def authenticate_user(data: LoginRequest, db: Session) -> dict:
    user = db.query(Auth).filter(Auth.email == data.email).first()
    if not user or not verify_password(data.password, user.password):
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Incorrect email or password',
        )
    access = create_access_token({'sub': user.email})
    refresh = create_refresh_token({'sub': user.email})
    payload = decode(
        access, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
    )
    return {
        'access_token': access,
        'refresh_token': refresh,
        'token_type': 'Bearer',
        'exp': payload.get('exp'),
        'iat': payload.get('iat') or int(time()),
        'user': {'id': user.id, 'email': user.email, 'role': user.role.value},
    }


def refresh_access_token(refresh_token: str) -> dict:
    try:
        payload = decode(
            refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        email = payload.get('sub')
        if not email:
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED,
                detail='Invalid refresh token',
            )
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED, detail='Refresh token expired'
        )
    except DecodeError:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED, detail='Invalid refresh token'
        )
    new_access = create_access_token({'sub': email})
    return {'access_token': new_access}
