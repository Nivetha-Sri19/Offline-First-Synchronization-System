from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RetryDecision:
    should_retry: bool
    next_attempt: int


class RetryService:
    def __init__(
        self,
        max_retries: int,
    ) -> None:
        self.max_retries = max_retries

    def evaluate(
        self,
        current_attempt: int,
    ) -> RetryDecision:
        next_attempt = current_attempt + 1

        return RetryDecision(
            should_retry=next_attempt <= self.max_retries,
            next_attempt=next_attempt,
        )