from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class ConflictResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    conflict_id: uuid.UUID
    record_id: uuid.UUID
    operation_id: uuid.UUID
    client_version: int
    server_version: int
    client_payload: dict[str, Any] | None
    server_payload: dict[str, Any] | None
    resolution_strategy: str | None
    status: str
    resolved_by: uuid.UUID | None
    resolved_at: datetime | None
    created_at: datetime


class ConflictListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    items: list[ConflictResponse]
    total: int
    page: int
    page_size: int
    total_pages: int