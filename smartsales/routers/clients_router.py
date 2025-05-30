from fastapi import APIRouter, Depends, status

from smartsales.controllers.clients_controller import (
    create_client_controller,
    delete_client_controller,
    list_clients,
    retrieve_client,
    update_client_controller,
)
from smartsales.core.security import get_current_user
from smartsales.schemas.clients_schema import (
    ClientListResponse,
    ClientResponse,
)

router = APIRouter(
    prefix='/clients',
    tags=['Clients'],
    dependencies=[Depends(get_current_user)],
)

router.get(
    '/', response_model=ClientListResponse, description='List all clients'
)(list_clients)
router.post(
    '/',
    response_model=ClientResponse,
    status_code=status.HTTP_201_CREATED,
    description='Create new client',
)(create_client_controller)
router.get(
    '/{client_id}',
    response_model=ClientResponse,
    description='Retrieve client',
)(retrieve_client)
router.put(
    '/{client_id}',
    response_model=ClientResponse,
    description='Update client',
)(update_client_controller)
router.delete(
    '/{client_id}',
    status_code=status.HTTP_204_NO_CONTENT,
    description='Delete client',
)(delete_client_controller)
