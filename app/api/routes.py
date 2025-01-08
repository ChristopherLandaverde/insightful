import logging
from datetime import datetime
from typing import Optional,List
from fastapi import HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from pydantic import BaseModel, ConfigDict
from app.db.base import get_db
from app.db.models import BaseExperiment, ExperimentData


logging.basicConfig(level=logging.INFO)

app = APIRouter()

class ExperimentBase(BaseModel):
    variant:str
    timestamp:datetime
    conversion:bool
    revenue:float=0.0
    engagement_minutes:float=0.0


class ExperimentVariantData(BaseModel):
    variant: str
    conversion: bool
    revenue: Optional[float] = 0.0
    engagement_minutes: Optional[float] = 0.0
    additional_data: Optional[str] = None

class ExperimentCreate(BaseModel):
    name: str
    description: str
    goal_metric: str
    experiment_type: str
    desired_outcome: str
    null_hypothesis: str
    alternative_hypothesis: str
    sample_size_group_a: int
    sample_size_group_b: int
    significance_level: float
    power: float
    bias_control_method: str
    identified_confounders: str
    success_metrics: str
    experiment_variants: List[ExperimentVariantData]  # This must be a list of ExperimentVariantData
# Response model for ExperimentData
class ExperimentDataResponse(BaseModel):

    id: int
    experiment_id: int
    variant: str
    timestamp: datetime
    conversion: bool
    revenue: float
    engagement_minutes: float
    additional_data: Optional[str]
    created_at: datetime
    updated_at: datetime

    # Enable ORM mode for SQLAlchemy serialization
    model_config = ConfigDict(from_attributes=True)

# Request model for ExperimentDataBase
class ExperimentDataBase(BaseModel):
    """
    ExperimentDataBase is a Pydantic model that represents the structure of experiment data for incoming requests.

    Attributes:
        name (str): The name of the experiment.
        description (Optional[str]): A brief description of the experiment.
        experiment_type (str): The type of the experiment.
        variant (str): The variant of the experiment.
        conversion (bool): Indicates if the experiment involves conversion.
        revenue (Optional[float]): The revenue generated from the experiment.
        engagement_minutes (Optional[float]): The engagement time in minutes.
        additional_data (Optional[str]): Any additional data related to the experiment.
    """
    name: str
    description: Optional[str]
    experiment_type: str
    variant: str
    conversion: bool
    revenue: Optional[float] = 0.0
    engagement_minutes: Optional[float] = 0.0
    additional_data: Optional[str] = None

# Response model for BaseExperiment
class ExperimentResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    experiment_type: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

@app.post("/experiment/")
def create_experiment(experiment: ExperimentCreate, db: Session = Depends(get_db)):
    logging.info("Incoming payload: %s", experiment.model_dump())


    # Create BaseExperiment entry
    new_experiment = BaseExperiment(
        name=experiment.name,
        description=experiment.description,
        goal_metric=experiment.goal_metric,
        experiment_type=experiment.experiment_type,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    db.add(new_experiment)
    db.commit()
    db.refresh(new_experiment)

    # Create ExperimentData entry
    experiment_data_entries=[]
    for variant_data in experiment.experiment_variants:
        new_experiment_data = ExperimentData( 
            experiment_id=new_experiment.id,
            variant=variant_data.variant,
            timestamp=datetime.now(),
            conversion=variant_data.conversion,
            revenue=variant_data.revenue,
            engagement_minutes=variant_data.engagement_minutes,
            additional_data=variant_data.additional_data,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db.add(new_experiment_data)
        experiment_data_entries.append(new_experiment_data)
    db.commit()

    # Return serialized response
    return {
    "experiment": ExperimentResponse.model_validate(new_experiment),
    "experiment_data": [ExperimentDataResponse.model_validate(data) for data in experiment_data_entries]
    }

@app.get("/experiment/{experiment_id}")
def get_experiment(experiment_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a experiment by its ID from the database.

    Args:
        experiment_id (int): The ID of the experiment to retrieve.
        db (Session): The database session dependency.

    Returns:
        dict: A dictionary containing the experiment data.

    Raises:
        HTTPException: If the experiment is not found, raises a 404 HTTP exception.
    """
    experiment = db.query(BaseExperiment).filter(BaseExperiment.id == experiment_id, BaseExperiment.deleted_at.is_(None)).first()
    if experiment is None:
        raise HTTPException(status_code=404, detail="Experiment not found")
    return ExperimentResponse.model_validate(experiment)

@app.delete("/experiment/{experiment_id}")
def soft_delete_experiment(experiment_id: int, db: Session = Depends(get_db)):
    """
    Soft delete a experiment by setting its `deleted_at` timestamp.

    Args:
        experiment_id (int): The ID of the experiment to be deleted.
        db (Session): The database session dependency.

    Returns:
        dict: A message indicating that the experiment has been deleted.

    Raises:
        HTTPException: If the experiment with the given ID is not found.
    """
    experiment = db.query(BaseExperiment).filter(BaseExperiment.id == experiment_id, BaseExperiment.deleted_at.is_(None)).first()
    if experiment is None:
        raise HTTPException(status_code=404, detail="Experiment not found")
    
    experiment.deleted_at = datetime.now()
    db.commit()
    return {"message": "Experiment deleted successfully"}

@app.get("/api/experiment/{experiment_id}/metrics/basic")
def get_experiment_basic_metrics(experiment_id: int, db: Session = Depends(get_db)):
    """
    Retrieve basic experiment metrics by experiment ID.

    Args:
        experiment_id (int): The ID of the experiment to retrieve metrics for.
        db (Session): The database session dependency.

    Returns:
        dict: A dictionary containing the basic experiment metrics.

    Raises:
        HTTPException: If the experiment is not found, raises a 404 HTTP exception.
    """
    experiment = db.query(BaseExperiment).filter(BaseExperiment.id == experiment_id, BaseExperiment.deleted_at.is_(None)).first()
    if not experiment:
        raise HTTPException(status_code=404, detail="Experiment not found")
    
    experiment_data=db.query(ExperimentData).filter(ExperimentData.experiment_id==experiment_id).all()
    if not experiment_data:
        raise HTTPException(status_code=404, detail="No experiment data found for the experiment")
    
    metrics={}

    for data in experiment_data:
        variant=data.variant
        if variant not in metrics:
            metrics[variant]={
                "total_revenue":0.0,
                "total_conversion":0,
                "total_entries":0,
                "total_engagement_minutes":0.0
            }
        metrics[variant]["total_revenue"]+=data.revenue
        metrics[variant]["total_conversion"]+=1 if data.conversion else 0
        metrics[variant]["total_entries"]+=1
        metrics[variant]["total_engagement_minutes"]+=data.engagement_minutes
    
    for variant,values in metrics.items():
        values["conversion_rate"]=(
            (values["total_conversion"]/values["total_entries"]) * 100
        ) if values["total_entries"]>0 else 0.0
        
        values["average_engagement_minutes"]=(
            values["total_engagement_minutes"]/values["total_entries"]
        ) if values["total_entries"]>0 else 0.0
    return {"experiment_id":experiment_id,"metrics":metrics}
        