from __future__ import annotations

from collections.abc import Generator
from contextlib import contextmanager
from typing import TypeVar

from sqlalchemy.orm import Session

T = TypeVar("T")


@contextmanager
def transactional_session(
    session: Session,
) -> Generator[Session, None, None]:
    """
    Execute a group of database operations as one transaction.

    The caller is responsible for supplying the session.

    On success:
        COMMIT

    On failure:
        ROLLBACK
        Re-raise the original exception
    """

    try:
        yield session
        session.commit()

    except Exception:
        session.rollback()
        raise


@contextmanager
def nested_transaction(
    session: Session,
) -> Generator[Session, None, None]:
    """
    Creates a SQLAlchemy SAVEPOINT.

    Useful when a service needs an isolated transactional section
    inside an already active transaction.
    """

    transaction = session.begin_nested()

    try:
        yield session
        transaction.commit()

    except Exception:
        transaction.rollback()
        raise