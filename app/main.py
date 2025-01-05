from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.base import init_db
from app.api.routes import app as routes_app

init_db()

app=FastAPI(title="Streaming Services API")
app.include_router(routes_app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """
    Asynchronous function that returns a greeting message.

    Returns:
        dict: A dictionary containing a greeting message.
    """
    return {"message": "Hello World"}