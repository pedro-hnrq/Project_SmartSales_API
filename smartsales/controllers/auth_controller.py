from fastapi import Depends
from sqlalchemy.orm import Session

from smartsales.core.database import get_session
from smartsales.schemas.auth_schema import (
    LoginRequest,
    LoginResponse,
    RefreshResponse,
    RegisterRequest,
    RegisterResponse,
    TokenRefreshRequest,
)
from smartsales.services.auth_service import (
    authenticate_user,
    refresh_access_token,
    register_user,
)


async def register_controller(
    body: RegisterRequest,
    session: Session = Depends(get_session),
) -> RegisterResponse:
    user = register_user(body, session)
    return RegisterResponse(
        name=user.name, email=user.email, role=user.role.value
    )


async def login_controller(
    body: LoginRequest,
    session: Session = Depends(get_session),
) -> LoginResponse:
    data = authenticate_user(body, session)
    return LoginResponse(**data)


async def refresh_controller(
    body: TokenRefreshRequest,
) -> RefreshResponse:
    data = refresh_access_token(body.refresh_token)
    return RefreshResponse(**data)
