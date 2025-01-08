from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class BaseExperiment(Base):
    """
    BaseExperiment model represents the base experiment entity in the database.

    Attributes:
        id (int): Primary key.
        experiment_type (str): Type of the experiment.
        created_at (datetime): Timestamp when the record was created.
        updated_at (datetime): Timestamp when the record was last updated.
        deleted_at (datetime, optional): Timestamp when the record was deleted.
        data (relationship): Relationship to the ExperimentData model.
    """
    __tablename__ = 'experiment'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    description = Column(String(255),nullable=True)
    goal_metric=Column(String(50))
    desired_outcome=Column(String(50),nullable=True)
    null_hypothesis=Column(String(50),nullable=True)
    alternative_hypothesis=Column(String(50),nullable=True)
    sample_size_group_a=Column(Integer,nullable=True)
    sample_size_group_b=Column(Integer,nullable=True)
    significance_level=Column(Float,default=0.05)
    power=Column(Float,default=0.80)
    bias_control_method=Column(String(50),nullable=True)
    identified_confounders=Column(String(50),nullable=True)
    success_metrics=Column(String(50),nullable=True)
    experiment_type = Column(String(50))
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    deleted_at = Column(DateTime, nullable=True)
    data = relationship("ExperimentData", back_populates='experiment')


class ExperimentData(Base):
    """
    ExerpimentData model represents the experiment data entity in the database.

    Attributes:
        id (int): Primary key.
        experiment_id (int): Foreign key referencing the BaseExperiment model.
        variant (str): Variant of the experiment.
        timestamp (datetime): Timestamp of the experiment data.
        conversion (bool): Indicates if the conversion happened.
        revenue (float): Revenue generated.
        engagement_minutes (float): Minutes of engagement.
        additional_data (JSONB): Additional data in JSONB format.
        created_at (datetime): Timestamp when the record was created.
        updated_at (datetime): Timestamp when the record was last updated.
        experiment (relationship): Relationship to the BaseExperiment model.
    """
    __tablename__ = 'experiment_data'
    id = Column(Integer, primary_key=True)
    experiment_id = Column(Integer, ForeignKey('experiment.id'))
    variant = Column(String(50), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    conversion = Column(Boolean, nullable=False)
    revenue = Column(Float, default=0.0)
    engagement_minutes = Column(Float, default=0.0)
    additional_data = Column(JSONB)
    user_id=Column(String(50),nullable=True)
    session_id=Column(String(50),nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    experimment = relationship("BaseExperiment", back_populates="data")

