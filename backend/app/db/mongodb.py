from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.core.config import get_settings


class MongoDB:
    """Small MongoDB connection holder for app startup and shutdown."""

    client: AsyncIOMotorClient | None = None
    database: AsyncIOMotorDatabase | None = None


mongodb = MongoDB()


async def connect_to_mongo() -> None:
    """Create the MongoDB client during FastAPI startup."""

    settings = get_settings()
    mongodb.client = AsyncIOMotorClient(settings.mongo_uri)
    mongodb.database = mongodb.client[settings.mongo_db_name]

    # Force an early ping so connection issues surface at startup.
    await mongodb.client.admin.command("ping")


async def close_mongo_connection() -> None:
    """Close the MongoDB client during FastAPI shutdown."""

    if mongodb.client is not None:
        mongodb.client.close()
        mongodb.client = None
        mongodb.database = None


def get_database() -> AsyncIOMotorDatabase:
    """Return the active MongoDB database instance for dependency injection."""

    if mongodb.database is None:
        raise RuntimeError("MongoDB database is not initialized")

    return mongodb.database
