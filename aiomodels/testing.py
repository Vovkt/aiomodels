from unittest import IsolatedAsyncioTestCase

from motor.motor_asyncio import AsyncIOMotorClient


class BaseTestModel(IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        db = AsyncIOMotorClient("mongodb://localhost/")
        await db.drop_database("test_aiomodels")
        self.client = db
        self.db = db["test_aiomodels"]
