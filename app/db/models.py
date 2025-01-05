from datetime import datetime
from sqlalchemy import Column, Integer, String,Float,DateTime,ForeignKey,Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base=declarative_base()

class BaseTest(Base):
    __tablename__='test'
    id=Column(Integer,primary_key=True)
    name=Column(String(50))
    description = Column(String(255))
    test_type=Column(String(50))
    created_at=Column(DateTime,default=datetime.now)
    updated_at=Column(DateTime,default=datetime.now,onupdate=datetime.now)
    deleted_at=Column(DateTime,nullable=True)
    

    data = relationship("TestData",back_populates='test')


class TestData(Base):
    __tablename__='test_data'
    id=Column(Integer,primary_key=True)
    test_id=Column(Integer,ForeignKey('test.id'))
    variant = Column(String(50),nullable=False)
    timestamp=Column(DateTime,nullable=False)
    conversion=Column(Boolean,nullable=False)
    revenue=Column(Float,default=0.0)
    engagement_minutes=Column(Float,default=0.0)
    additional_data=Column(String)
    created_at=Column(DateTime,default=datetime.now)
    updated_at=Column(DateTime,default=datetime.now,onupdate=datetime.now)

    test= relationship("BaseTest",back_populates="data")

BaseTest.data = relationship("TestData",back_populates='test')