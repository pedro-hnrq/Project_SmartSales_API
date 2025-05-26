from http import HTTPStatus

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.models import SecuritySchemeType
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer

from smartsales.routers.auth_router import router as auth_router
from smartsales.routers.clients_router import router as clients_router

# define o scheme de Bearer (JWT) para o OpenAPI
bearer_scheme = HTTPBearer(bearerFormat='JWT')

app = FastAPI(
    title='Project Smart Sales API',
    description='API',
    version='1.0.0',
)

# inclui seus routers normalmente
app.include_router(auth_router, prefix="/api")
app.include_router(clients_router, prefix="/api")


@app.get('/', status_code=HTTPStatus.OK)
def read_root():
    return {'message': 'Olá Mundo!'}


# handler para erros de validação (422) — retorna só {"message": ...}
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
):
    first_error = exc.errors()[0]
    msg = first_error.get('msg', 'Erro de validação')
    return JSONResponse(
        status_code=HTTPStatus.UNPROCESSABLE_ENTITY, content={'message': msg}
    )


# customiza o schema OpenAPI para usar apenas HTTP Bearer
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    # gera o OpenAPI padrão
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    # define o securityScheme BearerAuth
    openapi_schema['components']['securitySchemes'] = {
        'BearerAuth': {
            'type': SecuritySchemeType.http.value,
            'scheme': 'bearer',
            'bearerFormat': 'JWT',
        }
    }

    for path in openapi_schema['paths'].values():
        for operation in path.values():
            # sobrepõe qualquer security anterior
            operation['security'] = [{'BearerAuth': []}]

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi
