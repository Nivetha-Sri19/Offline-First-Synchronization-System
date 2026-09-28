from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict

from app.schemas.common import PaginationMeta


class RecordResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    owner_id: uuid.UUID
    data: dict[str, Any]
    version: int
    is_deleted: bool
    deleted_at: datetime | None
    created_at: datetime
    updated_at: datetime


class RecordListResponse(BaseModel):
    items: list[RecordResponse]
    pagination: PaginationMeta