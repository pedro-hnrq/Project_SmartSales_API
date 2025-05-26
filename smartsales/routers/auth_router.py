from fastapi import APIRouter

from smartsales.controllers.auth_controller import (
    login_controller,
    refresh_controller,
    register_controller,
)
from smartsales.schemas.auth_schema import (
    LoginResponse,
    RefreshResponse,
    RegisterResponse,
)

router = APIRouter(prefix='/token', tags=['Auth'])

router.post('/register', response_model=RegisterResponse)(register_controller)
router.post('/login', response_model=LoginResponse)(login_controller)
router.post('/refresh-token', response_model=RefreshResponse)(
    refresh_controller
)
