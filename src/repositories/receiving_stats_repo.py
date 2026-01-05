from __future__ import annotations

from sqlalchemy.orm import Session

from src.entities.receiving_stats import ReceivingStats
from src.repositories.base_repo import BaseRepository


class ReceivingStatsRepository(BaseRepository[ReceivingStats]):
    def __init__(self, session: Session) -> None:
        super().__init__(session=session, model=ReceivingStats)
