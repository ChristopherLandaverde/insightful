# This file manages the database engine, session, and table creation.

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.models import Base  

# Database URL for PostgRES
DATABASE_URL = "postgresql://user:password@db:5432/test_db"


# Create the database engine
engine = create_engine(
    DATABASE_URL # Required for POSTGRES
)

# Create a configured "SessionLocal" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create database tables
def init_db():
    """
    Initializes the database by creating all tables defined in the models.
    """
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully.")

# Dependency to get the database session
def get_db():
    """
    Provides a session for database interaction. Automatically closes the session after use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
