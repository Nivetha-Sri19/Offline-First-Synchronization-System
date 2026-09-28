from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query, status

from app.api.deps import get_current_user, get_record_service
from app.models.user import User
from app.schemas.record.request import (
    RecordCreateRequest,
    RecordDeleteRequest,
    RecordUpdateRequest,
)
from app.schemas.record.response import (
    RecordListResponse,
    RecordResponse,
)
from app.services.records.record_service import RecordService

router = APIRouter(
    prefix="/records",
    tags=["Records"],
)


@router.post(
    "",
    response_model=RecordResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_record(
    request: RecordCreateRequest,
    current_user: User = Depends(get_current_user),
    service: RecordService = Depends(get_record_service),
) -> RecordResponse:
    return service.create(
        owner_id=current_user.id,
        data=request.data,
    )


@router.get(
    "",
    response_model=RecordListResponse,
)
def list_records(
    search: str | None = Query(default=None, max_length=200),
    status_filter: str | None = Query(
        default=None,
        alias="status",
        max_length=30,
    ),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    sort_by: str = Query(default="updated_at"),
    sort_order: str = Query(default="desc", pattern="^(asc|desc)$"),
    current_user: User = Depends(get_current_user),
    service: RecordService = Depends(get_record_service),
) -> RecordListResponse:
    return service.list(
        owner_id=current_user.id,
        page=page,
        page_size=page_size,
        search=search,
        status=status_filter,
        sort_by=sort_by,
        sort_order=sort_order,
    )


@router.get(
    "/{record_id}",
    response_model=RecordResponse,
)
def get_record(
    record_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: RecordService = Depends(get_record_service),
) -> RecordResponse:
    return service.get(
        owner_id=current_user.id,
        record_id=record_id,
    )


@router.patch(
    "/{record_id}",
    response_model=RecordResponse,
)
def update_record(
    record_id: uuid.UUID,
    request: RecordUpdateRequest,
    current_user: User = Depends(get_current_user),
    service: RecordService = Depends(get_record_service),
) -> RecordResponse:
    return service.update(
        owner_id=current_user.id,
        record_id=record_id,
        data=request.data,
        expected_version=request.expected_version,
    )


@router.delete(
    "/{record_id}",
    response_model=RecordResponse,
)
def delete_record(
    record_id: uuid.UUID,
    request: RecordDeleteRequest,
    current_user: User = Depends(get_current_user),
    service: RecordService = Depends(get_record_service),
) -> RecordResponse:
    return service.delete(
        owner_id=current_user.id,
        record_id=record_id,
        expected_version=request.expected_version,
    )