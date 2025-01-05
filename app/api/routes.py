from datetime import datetime
from typing import Optional
from fastapi import HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from pydantic import BaseModel, ConfigDict
from app.db.base import get_db
from app.db.models import BaseTest, TestData

app = APIRouter()

# Response model for TestData
class TestDataResponse(BaseModel):
    """
    TestDataResponse is a Pydantic model that represents the structure of test data.

    Attributes:
        id (int): The ID of the test data.
        test_id (int): The ID of the test.
        variant (str): The variant of the test.
        timestamp (datetime): The timestamp of the test data.
        conversion (bool): Indicates if the conversion happened.
        revenue (float): The revenue generated.
        engagement_minutes (float): The engagement time in minutes.
        additional_data (Optional[str]): Any additional data related to the test.
        created_at (datetime): When the test data was created.
        updated_at (datetime): When the test data was last updated.
    """
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
def create_test(test: TestDataBase, db: Session = Depends(get_db)):
    """
    Create a new test and associated test data.

    Args:
        test (TestDataBase): The incoming test data request.
        db (Session): The database session dependency.

    Returns:
        dict: A dictionary containing the created test and test data.
    """
    # Create BaseTest entry
    new_test = BaseTest(
        name=test.name,
        description=test.description,
        test_type=test.test_type,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(new_test)
    db.commit()
    db.refresh(new_test)

    # Create TestData entry
    new_test_data = TestData(
        test_id=new_test.id,
        variant=test.variant,
        timestamp=datetime.utcnow(),
        conversion=test.conversion,
        revenue=test.revenue,
        engagement_minutes=test.engagement_minutes,
        additional_data=test.additional_data,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(new_test_data)
    db.commit()
    db.refresh(new_test_data)

    # Return serialized response
    return {
        "test": TestResponse.model_validate(new_test),
        "test_data": TestDataResponse.model_validate(new_test_data)
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
    
    test.deleted_at = datetime.utcnow()
    db.commit()
    return {"detail": "Test soft-deleted successfully"}
