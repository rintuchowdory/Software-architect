import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./software_architect.db")

DB_INIT_ERROR: str | None = None
engine = None
SessionLocal = None

try:
    connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
    engine = create_engine(DATABASE_URL, connect_args=connect_args)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
except Exception as e:  # noqa: BLE001
    DB_INIT_ERROR = f"{type(e).__name__}: {e}"

Base = declarative_base()


def get_db():
    if SessionLocal is None:
        raise RuntimeError(f"Database not initialized: {DB_INIT_ERROR}")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
