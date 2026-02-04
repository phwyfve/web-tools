from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorGridFSBucket
from beanie import init_beanie
from .config import settings
from .auth import User


# Global variables to store database connections
client = None
database = None
images_bucket = None

async def init_db():
    """Initialize database connection and models"""
    global client, database, images_bucket
    
    # Create motor client
    client = AsyncIOMotorClient(settings.mongodb_url)
    database = client[settings.database_name]
    
    # Initialize beanie with the User model
    await init_beanie(
        database=database,
        document_models=[User]
    )
    
    # Create GridFS bucket for images
    images_bucket = AsyncIOMotorGridFSBucket(database, bucket_name="images")

def get_images_bucket():
    """Get the images GridFS bucket"""
    return images_bucket

def get_database():
    """Get the database instance"""
    return database
