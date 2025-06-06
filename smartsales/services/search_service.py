# smartsales/services/search_service.py
from sqlalchemy.orm import Session

from smartsales.models.search import Search
from smartsales.schemas.search_schema import SearchCreate, SearchOut


class SearchService:
    @staticmethod
    def create_search(
        db: Session,
        search_in: SearchCreate,
        response: str,
        owner_id: int | None = None,
    ) -> SearchOut:
        """
        1) Cria e salva um Search no DB.
        2) Retorna a instância serializada como SearchOut.
        """
        new_search = Search(
            query=search_in.query, response=response, owner_id=owner_id
        )
        db.add(new_search)
        db.commit()
        db.refresh(new_search)
        return SearchOut.from_orm(new_search)
