from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql://user:password@localhost:5432/test_db"

# Create the engine
engine = create_engine(DATABASE_URL)

def test_connection():
    try:
        print("Testing database connection...")
        with engine.connect() as conn:
            print("Connection successful!")
            # Use `text()` for raw SQL queries
            result = conn.execute(text("SELECT 1"))
            print("Query result:", result.fetchone())
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    test_connection()
