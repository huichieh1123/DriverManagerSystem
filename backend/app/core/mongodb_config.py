from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os

load_dotenv() # Load environment variables from .env file

MONGO_DETAILS = os.getenv("MONGO_DETAILS")

if not MONGO_DETAILS:
    raise ValueError("MONGO_DETAILS environment variable not set.")

try:
    client = AsyncIOMotorClient(MONGO_DETAILS)
    # No direct ping() for AsyncIOMotorClient, connection is lazy
    print("MongoDB client initialized (connection is lazy)...")
    database = client.driver_manager_db # Your database name
    print(f"Connected to database: {database.name}")

    # Collections
    users_collection = database.get_collection("users_collection")
    jobs_collection = database.get_collection("jobs_collection")
    invitations_collection = database.get_collection("invitations_collection")
    vehicles_collection = database.get_collection("vehicles_collection")
    print("MongoDB collections initialized.")

except Exception as e:
    print(f"Error initializing MongoDB client: {e}")
    client = None
    database = None
    users_collection = None
    jobs_collection = None
    invitations_collection = None