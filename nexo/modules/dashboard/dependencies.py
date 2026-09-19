from typing import Generator
from nexo.core.db import SessionLocal


def get_db() -> Generator:
    """Dependency that yields a DB session and closes it after use."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
