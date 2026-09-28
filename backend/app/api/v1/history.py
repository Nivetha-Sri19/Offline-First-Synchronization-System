from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.sync_history import SyncHistory
from app.models.user import User
from app.schemas.sync.response import SyncHistoryResponse

router = APIRouter(
    prefix="/sync-history",
    tags=["Synchronization History"],
)


@router.get(
    "",
    response_model=list[SyncHistoryResponse],
)
def get_sync_history(
    status: str | None = Query(default=None),
    conflict_status: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[SyncHistory]:
    statement = select(SyncHistory).where(
        SyncHistory.user_id == current_user.id,
    )

    if status:
        statement = statement.where(
            SyncHistory.status == status,
        )

    if conflict_status:
        statement = statement.where(
            SyncHistory.conflict_status == conflict_status,
        )

    statement = (
        statement
        .order_by(SyncHistory.timestamp.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )

    return list(db.scalars(statement).all())