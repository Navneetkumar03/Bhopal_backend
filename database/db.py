"""
Database engine, session factory, and FastAPI dependency.
Reads configuration from config.py.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from config import setting


# ============ DATABASE ENGINE ============
# Create engine with connection pooling

engine = create_engine(
    setting.database_url,
    # echo=setting.debug,          # Print SQL only in debug mode
    pool_size=15,                # Base pool size
    max_overflow=10,              # Extra connections during bursts
    pool_pre_ping=True,          # Verify connection is alive
    pool_recycle=1800,           # Recycle after 30 min (prevents stale)
    pool_timeout=10,             # Wait max 10s for a free connection
    connect_args={
        "connect_timeout": 5,               # Fail fast if DB unreachable
        "application_name": "Bhopal_api",   # Shown in pg_stat_activity
    },
)


# ============ SESSION FACTORY ============
# Creates database sessions for each request

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


# ============ BASE MODEL CLASS ============
# All database models will inherit from this

Base = declarative_base()


# ============ FASTAPI DEPENDENCY ============

def get_db():
    """
    Dependency function for FastAPI routes.
    Creates a new database session for each request
    and automatically closes it when the request ends.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()