# app/api/v1/synchronization.py

from __future__ import annotations

import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, Query, status

from app.api.deps import get_current_user, get_sync_service
from app.models.user import User
from app.schemas.conflict.request import ConflictResolutionRequest
from app.schemas.conflict.response import ConflictResponse
from app.schemas.sync.request import SyncBatchRequest
from app.schemas.sync.response import (
    SyncBatchResponse,
    SyncConflictListResponse,
    SyncHistoryListResponse,
    SyncPullResponse,
    SyncStatusResponse,
)
from app.services.synchronization.sync_service import SyncService

router = APIRouter(
    prefix="/sync",
    tags=["Synchronization"],
)


@router.get(
    "/pull",
    response_model=SyncPullResponse,
)
def pull(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=100, ge=1, le=500),
    updated_since: datetime | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    service: SyncService = Depends(get_sync_service),
) -> SyncPullResponse:
    return service.pull(
        user_id=current_user.id,
        page=page,
        page_size=page_size,
        updated_since=updated_since,
    )


@router.post(
    "/push",
    response_model=SyncBatchResponse,
    status_code=status.HTTP_200_OK,
)
def push(
    request: SyncBatchRequest,
    current_user: User = Depends(get_current_user),
    service: SyncService = Depends(get_sync_service),
) -> SyncBatchResponse:
    return service.process_batch(
        user_id=current_user.id,
        request=request,
    )


@router.get(
    "/conflicts",
    response_model=SyncConflictListResponse,
)
def get_conflicts(
    conflict_status: str | None = Query(
        default=None,
        alias="status",
    ),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    service: SyncService = Depends(get_sync_service),
) -> SyncConflictListResponse:
    return service.list_conflicts(
        user_id=current_user.id,
        page=page,
        page_size=page_size,
        status=conflict_status,
    )


@router.post(
    "/conflicts/{conflict_id}/resolve",
    response_model=ConflictResponse,
)
def resolve_conflict(
    conflict_id: uuid.UUID,
    request: ConflictResolutionRequest,
    current_user: User = Depends(get_current_user),
    service: SyncService = Depends(get_sync_service),
) -> ConflictResponse:
    return service.resolve_conflict(
        user_id=current_user.id,
        conflict_id=conflict_id,
        request=request,
    )


@router.get(
    "/history",
    response_model=SyncHistoryListResponse,
)
def get_history(
    status_filter: str | None = Query(
        default=None,
        alias="status",
    ),
    conflict_status: str | None = Query(default=None),
    operation_type: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    service: SyncService = Depends(get_sync_service),
) -> SyncHistoryListResponse:
    return service.history(
        user_id=current_user.id,
        page=page,
        page_size=page_size,
        status=status_filter,
        conflict_status=conflict_status,
        operation_type=operation_type,
    )


@router.get(
    "/status",
    response_model=SyncStatusResponse,
)
def get_sync_status(
    current_user: User = Depends(get_current_user),
    service: SyncService = Depends(get_sync_service),
) -> SyncStatusResponse:
    return service.status(
        user_id=current_user.id,
    )