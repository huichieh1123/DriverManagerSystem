from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from app.api.v1.endpoints import tasks, users, jobs, companies, dispatchers, drivers

app = FastAPI(title="Driver Manager System API")

# CORS Middleware
# Allow origins from environment variable (for Render deployment)
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173") # Default to localhost for local development
origins = [
    FRONTEND_URL,
    "http://localhost:5173", # For local frontend development
    "http://127.0.0.1:5173", # For local frontend development
    "https://driver-manager-system.netlify.app", # For production frontend deployment

]

print("CORS allowed origins:", origins)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(tasks.router, prefix="/api/v1", tags=["tasks"])
app.include_router(users.router, prefix="/api/v1", tags=["users"])
app.include_router(companies.router, prefix="/api/v1/companies", tags=["companies"])
app.include_router(dispatchers.router, prefix="/api/v1/dispatchers", tags=["dispatchers"])
app.include_router(drivers.router, prefix="/api/v1/drivers", tags=["drivers"])
app.include_router(jobs.router, prefix="/api/v1", tags=["jobs"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the Driver Manager System API"}