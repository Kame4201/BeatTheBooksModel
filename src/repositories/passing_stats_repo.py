from __future__ import annotations

from sqlalchemy.orm import Session

from src.entities.passing_stats import PassingStats
from src.repositories.base_repo import BaseRepository


class PassingStatsRepository(BaseRepository[PassingStats]):
    def __init__(self, session: Session) -> None:
        super().__init__(session=session, model=PassingStats)
