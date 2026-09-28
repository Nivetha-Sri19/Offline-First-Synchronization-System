from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class VersionCheckResult:
    matches: bool
    client_version: int
    server_version: int


class VersionService:
    @staticmethod
    def check(
        *,
        client_version: int,
        server_version: int,
    ) -> VersionCheckResult:
        return VersionCheckResult(
            matches=client_version == server_version,
            client_version=client_version,
            server_version=server_version,
        )