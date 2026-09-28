from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends

from app.api.deps import get_conflict_service, get_current_user
from app.models.user import User
from app.schemas.conflict.request import ConflictResolutionRequest
from app.schemas.conflict.response import (
    ConflictListResponse,
    ConflictResponse,
)
from app.services.conflicts.conflict_service import ConflictService

router = APIRouter(
    prefix="/conflicts",
    tags=["Conflicts"],
)


@router.get(
    "",
    response_model=ConflictListResponse,
)
def list_conflicts(
    status: str | None = None,
    page: int = 1,
    page_size: int = 20,
    current_user: User = Depends(get_current_user),
    service: ConflictService = Depends(get_conflict_service),
) -> ConflictListResponse:
    return service.list(
        user_id=current_user.id,
        page=page,
        page_size=page_size,
        status=status,
    )


@router.post(
    "/{conflict_id}/resolve",
    response_model=ConflictResponse,
)
def resolve_conflict(
    conflict_id: uuid.UUID,
    request: ConflictResolutionRequest,
    current_user: User = Depends(get_current_user),
    service: ConflictService = Depends(get_conflict_service),
) -> ConflictResponse:
    return service.resolve(
        user_id=current_user.id,
        conflict_id=conflict_id,
        request=request,
    )