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
except Exception as e:  # noqa: BLE001
    DB_INIT_ERROR = f"{type(e).__name__}: {e}"
    engine = None

# When running on Postgres, make sure the dedicated application schema exists
# before anything (e.g. Base.metadata.create_all in main.py) creates tables.
# This lets the app share a Postgres instance with other projects without
# colliding on common table names (users, projects, ...).
if engine is not None and DATABASE_URL.startswith("postgresql"):
    try:
        with engine.connect() as conn:
            conn.exec_driver_sql(
                f'CREATE SCHEMA IF NOT EXISTS "{os.getenv("DB_SCHEMA", "software_architect")}"'
            )
            conn.commit()
    except Exception as e:  # noqa: BLE001
        DB_INIT_ERROR = f"schema init failed: {type(e).__name__}: {e}"
        engine = None

if engine is not None:
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    if SessionLocal is None:
        raise RuntimeError(f"Database not initialized: {DB_INIT_ERROR}")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
