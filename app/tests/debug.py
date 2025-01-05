from sqlalchemy import create_engine, Column, Integer, String, Boolean, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

# Initialize Base and Engine
Base = declarative_base()
engine = create_engine("sqlite:///./test.db", echo=True)

# Define Models
class Test(Base):
    __tablename__ = "test"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String)
    test_type = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class TestData(Base):
    __tablename__ = "test_data"
    id = Column(Integer, primary_key=True, index=True)
    test_id = Column(Integer)
    variant = Column(String, nullable=False)
    conversion = Column(Boolean, default=False)
    revenue = Column(Float, default=0.0)
    engagement_minutes = Column(Float, default=0.0)
    additional_data = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Drop and Recreate Tables
Base.metadata.drop_all(bind=engine)
print("All tables dropped.")
Base.metadata.create_all(bind=engine)
print("All tables recreated successfully.")
