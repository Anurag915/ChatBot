import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def test_connect():
    uri = "mongodb+srv://prajapatianurag0905_db_user:9KARcMf8XulrQl3x@cluster0.wby3m8f.mongodb.net/?appName=Cluster0"
    print("Connecting to MongoDB Atlas...")
    try:
        client = AsyncIOMotorClient(uri)
        await client.admin.command("ping")
        print("Success! Pinged MongoDB Atlas successfully.")
    except Exception as e:
        print("Error connecting:", e)

asyncio.run(test_connect())
