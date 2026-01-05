from __future__ import annotations

from sqlalchemy.orm import Session

from src.entities.team_offense import TeamOffense
from src.repositories.base_repo import BaseRepository


class TeamOffenseRepository(BaseRepository[TeamOffense]):
    def __init__(self, session: Session) -> None:
        super().__init__(session=session, model=TeamOffense)
