from fastapi.testclient import TestClient
from app.main import app
from app.db.base import get_db
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
import pytest

SQLALCHEMY_DATABASE_URL = "postgresql://user:password@localhost:5432/test_db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

@pytest.fixture(scope="function", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

test_id = None

def test_create_test():
    global test_id
    test_payload = {
        "name": "Test A/B Campaign",
        "description": "Testing conversion rates for new page design",
        "goal_metric": "conversion_rate",
        "test_type": "engagement",
        "desired_outcome": "Increase conversion by 10%",
        "null_hypothesis": "No significant difference in conversion rates",
        "alternative_hypothesis": "Treatment improves conversion rates",
        "sample_size_group_a": 1000,
        "sample_size_group_b": 1000,
        "significance_level": 0.05,
        "power": 0.8,
        "bias_control_method": "random_assignment",
        "identified_confounders": "None identified",
        "success_metrics": "conversion_rate",
        "test_variants": [
            {
                "variant": "A",
                "conversion": False,
                "revenue": 0.0,
                "engagement_minutes": 0.0,
                "additional_data": None,
            },
            {
                "variant": "B",
                "conversion": True,
                "revenue": 100.0,
                "engagement_minutes": 5.0,
                "additional_data": "Test group B details",
            }
        ]
    }

    response = client.post("/test/", json=test_payload)
    assert response.status_code == 200
    data = response.json()
    test_id = data["test"]["id"]
    assert data["test"]["name"] == "Test A/B Campaign"
    assert len(data["test_data"]) == 2

def test_get_test():
    response = client.get(f"/test/{test_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test A/B Campaign"

def test_basic_metrics():
     print(f"[DEBUG] Test ID in test_basic_metrics: {test_id}")
     response = client.get(f"/api/test/{test_id}/metrics/basic")
     print(f"Response content: {response.json()}")
     assert response.status_code == 200
     data = response.json()
     assert data["test_id"] == test_id
     assert "A" in data["metrics"]
     assert data["metrics"]["A"]["total_revenue"] == 0.0
     assert data["metrics"]["A"]["total_conversion"] == 0
     assert data["metrics"]["A"]["total_entries"] == 1
     assert data["metrics"]["A"]["total_engagement_minutes"] == 0.0
     assert data["metrics"]["A"]["conversion_rate"] == 0.0
     
     assert data["metrics"]["A"]["average_engagement_minutes"] == 0.0
     
     assert "B" in data["metrics"]
     assert data["metrics"]["B"]["total_revenue"] == 100.0
     assert data["metrics"]["B"]["total_conversion"] == 1
     assert data["metrics"]["B"]["total_entries"] == 1
     assert data["metrics"]["B"]["total_engagement_minutes"] == 5.0
     assert data["metrics"]["B"]["conversion_rate"] == 100.0
     assert data["metrics"]["B"]["average_engagement_minutes"] == 5.0

def test_soft_delete_test():
    response = client.delete(f"/test/{test_id}")
    assert response.status_code == 200
    data = response.json()
    print(f"Response content: {data}")
    
    # Normalize and strip before comparison
    assert data["message"].strip() == "Test deleted successfully", f"Mismatch: {data['message']} != 'Test deleted successfully'"

    # Verify test is not retrievable
    response = client.get(f"/test/{test_id}")
    assert response.status_code == 404



