import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./software_architect.db")

# SQLAlchemy 2.0 dropped support for the legacy "postgres://" scheme that
# Render (and Heroku-style providers before it) still hand out in their
# generated connection strings. Without this, create_engine() raises
# NoSuchModuleError and the app falls back to DB_INIT_ERROR on every request.
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

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
