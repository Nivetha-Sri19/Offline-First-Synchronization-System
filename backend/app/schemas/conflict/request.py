from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ConflictResolutionStrategy(str, Enum):
    SERVER_WINS = "server_wins"
    CLIENT_WINS = "client_wins"
    LAST_WRITE_WINS = "last_write_wins"
    MANUAL = "manual"


class ConflictResolutionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    strategy: ConflictResolutionStrategy
    resolved_data: dict[str, Any] | None = None

    @property
    def requires_manual_data(self) -> bool:
        return self.strategy == ConflictResolutionStrategy.MANUAL


class ConflictFilterRequest(BaseModel):
    status: str | None = Field(default=None, max_length=30)
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)