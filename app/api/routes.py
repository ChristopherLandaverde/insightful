from datetime import datetime
from typing import Optional
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.db.base import get_db
from app.db.models import BaseTest,TestData



app = FastAPI()

class TestDataBase(BaseModel):
    """
    TestDataBase is a Pydantic model that represents the structure of test data.

    Attributes:
        name (str): The name of the test.
        description (Optional[str]): A brief description of the test. Default is None.
        test_type (str): The type of the test.
        variant (str): The variant of the test.
        conversion (bool): Indicates if the test involves conversion.
        revenue (Optional[float]): The revenue generated from the test. Default is 0.0.
        engagement_minutes (Optional[float]): The engagement time in minutes. Default is 0.0.
        additional_data (Optional[str]): Any additional data related to the test. Default is None.
    """
    name:str
    description: Optional[str]
    test_type:str
    variant:str
    conversion:bool
    revenue:Optional[float]=0.0
    engagement_minutes:Optional[float]=0.0
    additional_data:Optional[str] = None


@app.post("/test/")

def create_test(test: TestDataBase,db: Session = Depends(get_db)):
    new_test=BaseTest(
        name = test.name,
        description = test.description,
        test_type = test.test_type,
        created_date=  datetime.now(),
        updated_at= datetime.now()
    )
    db.add(new_test)
    db.commit()
    db.refresh(new_test)

    new_test_data=TestData(
        test_id=new_test.id,
        variant=test.variant,
        timestamp=datetime.now(),
        conversion=test.conversion,
        revenue=test.revenue,
        engagement_minutes=test.engagement_minutes,
        additional_data=test.additional_data
    )
    db.add(new_test_data)
    db.commit()
    db.refresh(new_test_data)

    return {"test":new_test,"test_data":new_test_data}
    
@app.get("/test/{test_id}")
def get_test(test_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a test by its ID from the database.

    Args:
        test_id (int): The ID of the test to retrieve.
        db (Session, optional): The database session dependency. Defaults to Depends(get_db).

    Returns:
        BaseTest: The test object if found.

    Raises:
        HTTPException: If the test is not found, raises a 404 HTTP exception with the message "Test not found".
    """
    test = db.query(BaseTest).filter(BaseTest.id == test_id, BaseTest.deleted_at is None).first()
    if test is None:
        raise HTTPException(status_code=404, detail="Test not found")
    return test

@app.delete("/test/{test_id}")
def soft_delete_test(test_id: int, db: Session = Depends(get_db)):
    """
    Soft delete a test by setting its `deleted_at` timestamp.

    Args:
        test_id (int): The ID of the test to be deleted.
        db (Session): The database session dependency.

    Raises:
        HTTPException: If the test with the given ID is not found.

    Returns:
        dict: A message indicating that the test has been deleted.
    """
