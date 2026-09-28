from __future__ import annotations

from collections.abc import Generator

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker


class DatabaseSessionManager:
    def __init__(
        self,
        database_url: str,
        *,
        pool_size: int = 10,
        max_overflow: int = 20,
        pool_timeout: int = 30,
        pool_recycle: int = 1800,
        echo: bool = False,
    ) -> None:
        self.engine: Engine = create_engine(
            database_url,
            pool_pre_ping=True,
            pool_recycle=pool_recycle,
            pool_size=pool_size,
            max_overflow=max_overflow,
            pool_timeout=pool_timeout,
            echo=echo,
            future=True,
        )

        self.session_factory = sessionmaker(
            bind=self.engine,
            class_=Session,
            autoflush=False,
            expire_on_commit=False,
            autocommit=False,
        )

    def get_session(self) -> Session:
        return self.session_factory()

    def session_dependency(self) -> Generator[Session, None, None]:
        session = self.get_session()

        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def dispose(self) -> None:
        self.engine.dispose()