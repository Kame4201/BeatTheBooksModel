from __future__ import annotations

from sqlalchemy.orm import Session

from src.entities.rushing_stats import RushingStats
from src.repositories.base_repo import BaseRepository


class RushingStatsRepository(BaseRepository[RushingStats]):
    def __init__(self, session: Session) -> None:
        super().__init__(session=session, model=RushingStats)
