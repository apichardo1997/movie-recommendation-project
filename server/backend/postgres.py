import contextlib
from typing import Any, Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from server.backend.config import config


class PostgresSessionManager:
    def __init__(self, engine_kwargs: dict[str, Any] | None = None):
        if engine_kwargs is None:
            engine_kwargs = {}
        self.engine = create_engine(config.postgres_dns, **engine_kwargs)
        self.sessionmaker = sessionmaker(
            autocommit=False,
            bind=self.engine,
            autoflush=False,
            expire_on_commit=False,
        )

    def close(self):
        if self.engine is None:
            raise Exception("DatabaseSessionManager is not initialized")
        self.engine.dispose()

        self.engine = None
        self.sessionmaker = None

    @contextlib.contextmanager
    def open_session(self) -> Generator[Session, None, None]:
        if self.sessionmaker is None:
            raise Exception("DatabaseSessionManager is not initialized")

        session = self.sessionmaker()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
