from datetime import datetime, timedelta
from http import HTTPStatus
from zoneinfo import ZoneInfo

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import DecodeError, ExpiredSignatureError, decode, encode
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.orm import Session

from smartsales.core.database import get_session
from smartsales.core.settings import Settings
from smartsales.models.auth import Auth

settings = Settings()
pwd_context = PasswordHash.recommended()

bearer_scheme = HTTPBearer(bearerFormat='JWT')


def create_access_token(data: dict):
    now = datetime.now(tz=ZoneInfo('UTC'))
    expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = data.copy()
    to_encode.update({
        'iat': int(now.timestamp()),
        'exp': int(expire.timestamp()),
    })
    return encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def get_password_hash(password: str):
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)


def create_refresh_token(data: dict):
    expire = datetime.now(tz=ZoneInfo('UTC')) + timedelta(days=7)
    to_encode = data.copy()
    to_encode.update({'exp': expire})
    return encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    session: Session = Depends(get_session),
) -> Auth:
    token = credentials.credentials
    credentials_exception = HTTPException(
        status_code=HTTPStatus.UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'},
    )

    try:
        payload = decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        subject_email = payload.get('sub')
        if not subject_email:
            raise credentials_exception
    except (DecodeError, ExpiredSignatureError):
        raise credentials_exception

    # aqui é síncrono, sem await
    user = session.scalar(select(Auth).where(Auth.email == subject_email))
    if not user:
        raise credentials_exception

    return user
