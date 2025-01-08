# Insightful

**Goal:** Simplify marketing science with a friendly UI that scales from basic to advanced. Keep track of all your tests to discover what works for your brand—and what doesn't.

---

## Key Features

- **Experiment Setup**: Define tests with details like goal metrics, hypotheses, sample sizes, significance levels, and bias control methods.
- **Data Collection**: Upload and manage data for test variants, including conversions, revenue, and engagement metrics.
- **CRUD Operations**: Create, retrieve, update, and delete tests and related data via API endpoints.
- **Soft Deletes**: Preserve test records for audit purposes with soft deletion functionality.
- **Database Integration**: Uses PostgreSQL (or SQLite in development) to store and manage test data efficiently.

---

## Tech Stack

- **Backend**: FastAPI
- **Database**: PostgreSQL (or SQLite in development)
- **ORM**: SQLAlchemy
- **Models**: Pydantic for request/response validation
- **CORS**: Enabled for flexible frontend integration

---

## Endpoints Overview

### Root
- **GET /**: Test server health.

### Test Management
- **POST /test/**: Create a new A/B test.
- **GET /test/{test_id}**: Retrieve details of an A/B test by ID.
- **DELETE /test/{test_id}**: Soft delete an A/B test.


