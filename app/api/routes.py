import logging
from datetime import datetime
from typing import Optional,List
from fastapi import HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from pydantic import BaseModel, ConfigDict
from app.db.base import get_db
from app.db.models import BaseTest, TestData


logging.basicConfig(level=logging.INFO)

app = APIRouter()

class TestBase(BaseModel):
    variant:str
    timestamp:datetime
    conversion:bool
    revenue:float=0.0
    engagement_minutes:float=0.0


class TestVariantData(BaseModel):
    variant: str
    conversion: bool
    revenue: Optional[float] = 0.0
    engagement_minutes: Optional[float] = 0.0
    additional_data: Optional[str] = None

class TestCreate(BaseModel):
    name: str
    description: str
    goal_metric: str
    test_type: str
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
    test_variants: List[TestVariantData]  # This must be a list of TestVariantData
# Response model for TestData
class TestDataResponse(BaseModel):

    id: int
    test_id: int
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

# Request model for TestDataBase
class TestDataBase(BaseModel):
    """
    TestDataBase is a Pydantic model that represents the structure of test data for incoming requests.

    Attributes:
        name (str): The name of the test.
        description (Optional[str]): A brief description of the test.
        test_type (str): The type of the test.
        variant (str): The variant of the test.
        conversion (bool): Indicates if the test involves conversion.
        revenue (Optional[float]): The revenue generated from the test.
        engagement_minutes (Optional[float]): The engagement time in minutes.
        additional_data (Optional[str]): Any additional data related to the test.
    """
    name: str
    description: Optional[str]
    test_type: str
    variant: str
    conversion: bool
    revenue: Optional[float] = 0.0
    engagement_minutes: Optional[float] = 0.0
    additional_data: Optional[str] = None

# Response model for BaseTest
class TestResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    test_type: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

@app.post("/test/")
def create_test(test: TestCreate, db: Session = Depends(get_db)):
    logging.info("Incoming payload: %s", test.model_dump())


    # Create BaseTest entry
    new_test = BaseTest(
        name=test.name,
        description=test.description,
        goal_metric=test.goal_metric,
        test_type=test.test_type,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    db.add(new_test)
    db.commit()
    db.refresh(new_test)

    # Create TestData entry
    test_data_entries=[]
    for variant_data in test.test_variants:
        new_test_data = TestData( 
            test_id=new_test.id,
            variant=variant_data.variant,
            timestamp=datetime.now(),
            conversion=variant_data.conversion,
            revenue=variant_data.revenue,
            engagement_minutes=variant_data.engagement_minutes,
            additional_data=variant_data.additional_data,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db.add(new_test_data)
        test_data_entries.append(new_test_data)
    db.commit()

    # Return serialized response
    return {
    "test": TestResponse.model_validate(new_test),
    "test_data": [TestDataResponse.model_validate(data) for data in test_data_entries]
    }

@app.get("/test/{test_id}")
def get_test(test_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a test by its ID from the database.

    Args:
        test_id (int): The ID of the test to retrieve.
        db (Session): The database session dependency.

    Returns:
        dict: A dictionary containing the test data.

    Raises:
        HTTPException: If the test is not found, raises a 404 HTTP exception.
    """
    test = db.query(BaseTest).filter(BaseTest.id == test_id, BaseTest.deleted_at.is_(None)).first()
    if test is None:
        raise HTTPException(status_code=404, detail="Test not found")
    return TestResponse.model_validate(test)

@app.delete("/test/{test_id}")
def soft_delete_test(test_id: int, db: Session = Depends(get_db)):
    """
    Soft delete a test by setting its `deleted_at` timestamp.

    Args:
        test_id (int): The ID of the test to be deleted.
        db (Session): The database session dependency.

    Returns:
        dict: A message indicating that the test has been deleted.

    Raises:
        HTTPException: If the test with the given ID is not found.
    """
    test = db.query(BaseTest).filter(BaseTest.id == test_id, BaseTest.deleted_at.is_(None)).first()
    if test is None:
        raise HTTPException(status_code=404, detail="Test not found")
    
    test.deleted_at = datetime.now()
    db.commit()
    return {"message": "Test deleted successfully"}

@app.get("/api/test/{test_id}/metrics/basic")
def get_test_basic_metrics(test_id: int, db: Session = Depends(get_db)):
    """
    Retrieve basic test metrics by test ID.

    Args:
        test_id (int): The ID of the test to retrieve metrics for.
        db (Session): The database session dependency.

    Returns:
        dict: A dictionary containing the basic test metrics.

    Raises:
        HTTPException: If the test is not found, raises a 404 HTTP exception.
    """
    test = db.query(BaseTest).filter(BaseTest.id == test_id, BaseTest.deleted_at.is_(None)).first()
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    
    test_data=db.query(TestData).filter(TestData.test_id==test_id).all()
    if not test_data:
        raise HTTPException(status_code=404, detail="No test data found for the test")
    
    metrics={}

    for data in test_data:
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
    return {"test_id":test_id,"metrics":metrics}
        