# Variables
DB_USER = user             
DB_PASSWORD = password     
DB_NAME = test_db                                  
DB_HOST = localhost        
DB_PORT = 5432 

.PHONY: all
all: connect_to_table


 
.PHONY: connect_to_table
connect_to_table:
	psql -U $(DB_USER) -d $(DB_NAME) -h $(DB_HOST) -p $(DB_PORT) -c "SELECT * FROM test;"

 
.PHONY: check_connection
check_connection:
	psql -U $(DB_USER) -d $(DB_NAME) -h $(DB_HOST) -p $(DB_PORT) -c "\conninfo"

 
.PHONY: list_tables
list_tables:
	psql -U $(DB_USER) -d $(DB_NAME) -h $(DB_HOST) -p $(DB_PORT) -c "\dt"

 
.PHONY: describe_table
describe_table:
	psql -U $(DB_USER) -d $(DB_NAME) -h $(DB_HOST) -p $(DB_PORT) -c "\d test"
# Create the database
create-db:
	@echo "Creating database $(DB_NAME)..."
	@PGPASSWORD=$(DB_PASSWORD) psql -U $(DB_USER) -h $(DB_HOST) -p $(DB_PORT) -d postgres -c "CREATE DATABASE $(DB_NAME);"
	@echo "Database $(DB_NAME) created successfully!"

 
drop-db:
	@echo "Dropping database $(DB_NAME)..."
	@PGPASSWORD=$(DB_PASSWORD) psql -U $(DB_USER) -h $(DB_HOST) -p $(DB_PORT) -d postgres -c "DROP DATABASE IF EXISTS $(DB_NAME);"
	@echo "Database $(DB_NAME) dropped successfully!"

# Show databases
show-databases:# ...existing code...
	@PGPASSWORD=$(DB_PASS) psql -U $(DB_USER) -h $(DB_HOST) -p $(DB_PORT) -c "\l"

# Connect to the database
connect-db:
	@echo "Connecting to database $(DB_NAME)..."
	@PGPASSWORD=$(DB_PASSWORD) psql -U $(DB_USER) -h $(DB_HOST) -p $(DB_PORT) $(DB_NAME)

# Run migrations with Alembic
migrate:
	@echo "Running Alembic migrations..."
	@alembic upgrade head
	@echo "Migrations completed successfully!"

# Check database status
status:
	@echo "Checking PostgreSQL service status..."
	@pg_isready -h $(DB_HOST) -p $(DB_PORT) -U $(DB_USER)

connect:
	@echo "Connecting to database $(DB_NAME)..."



# Run the FastAPI app
run:
	@echo "Starting FastAPI app..."
	uvicorn app.main:app --reload

# Help menu
help:
	@echo "Available commands:"
	@echo " make create-db    - Create the PostgreSQL database"
	@echo "  make drop-db      - Drop the PostgreSQL database"
	@echo "  make connect-db   - Connect to the PostgreSQL database"
	@echo "  make migrate      - Run Alembic migrations"
	@echo "  make status       - Check the PostgreSQL service status"
	@echo "  make list_tables      - List all tables in the database"
	@echo "  make describe_table   - Show structure of table"
	@echo "  make show-databases   - List all available databases"
	@echo "  make check_connection - Show current connection info"
	@echo "  make run              - Start the FastAPI application"
