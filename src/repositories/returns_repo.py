from __future__ import annotations

from sqlalchemy.orm import Session

from src.entities.returns import Returns
from src.repositories.base_repo import BaseRepository


class ReturnsRepository(BaseRepository[Returns]):
    def __init__(self, session: Session) -> None:
        super().__init__(session=session, model=Returns)
