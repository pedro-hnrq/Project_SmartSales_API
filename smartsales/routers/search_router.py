from fastapi import APIRouter

from smartsales.controllers.search_controller import search_query
from smartsales.schemas.search_schema import SearchOut

router = APIRouter(prefix='/search', tags=['Search'])

router.get(
    '/',
    response_model=SearchOut,
    description='Realiza busca usando Groq/Llama no SmartSales',
)(search_query)
