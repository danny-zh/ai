"""Database engine and request-scoped session configuration."""

from __future__ import annotations

import os
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker


def get_database_url() -> str:
    """Return the required database connection URL.

    Returns:
        MySQL SQLAlchemy connection URL.

    Raises:
        RuntimeError: If DATABASE_URL is not configured.
    """
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL must be configured")
    return database_url


def create_database_engine() -> Engine:
    """Create an SQLAlchemy engine for the configured database.

    Returns:
        Configured SQLAlchemy engine.
    """
    return create_engine(get_database_url(), pool_pre_ping=True)


def create_session_factory(engine: Engine) -> sessionmaker[Session]:
    """Create a session factory for an engine.

    Args:
        engine: SQLAlchemy engine used to create sessions.

    Returns:
        Session factory with explicit transaction commits.
    """
    return sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_session() -> Generator[Session, None, None]:
    """Yield a database session for one request.

    Yields:
        Open SQLAlchemy session that is closed after the request.
    """
    session = create_session_factory(create_database_engine())()
    try:
        yield session
    finally:
        session.close()