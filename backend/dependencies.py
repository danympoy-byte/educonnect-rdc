"""
Shared dependencies to avoid circular imports
"""
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from pathlib import Path
import os

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB configuration
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "educonnect")

# Global database client and database
client = None
db = None

def init_database():
    """Initialize database connection"""
    global client, db
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    return db

def get_db():
    """Get database instance"""
    global db
    if db is None:
        init_database()
    return db
