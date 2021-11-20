from unittest import IsolatedAsyncioTestCase

from motor.motor_asyncio import AsyncIOMotorClient

from aiomodel.model import Model


class BaseTestModel(IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        db = AsyncIOMotorClient("mongodb://localhost/")
        await db.drop_database("test_aiomodel")
        self.db = db["test_aiomodel"]


class TestModelRead(BaseTestModel):
    async def test_read_by_object_id(self):
        model = Model(self.db, collection_name="users")
        result = await model.collection.insert_one({"name": "vovkt"})
        _id = result.inserted_id

        actual = await model.read_one(_id)
        self.assertEqual({"_id": _id, "name": "vovkt"}, actual)

    async def test_read_by_string_instead_object_id(self):
        model = Model(self.db, collection_name="users")
        result = await model.collection.insert_one({"name": "vovkt"})
        _id = result.inserted_id

        actual = await model.read_one(str(_id), strict=False)
        self.assertIsNone(actual)

    async def test_read_by_query_by_object_id(self):
        model = Model(self.db, collection_name="users")
        result = await model.collection.insert_one({"name": "vovkt"})
        _id = result.inserted_id

        actual = await model.read_one({"_id": _id})
        self.assertEqual({"_id": _id, "name": "vovkt"}, actual)

    async def test_read_by_query_by_string(self):
        model = Model(self.db, collection_name="users")
        result = await model.collection.insert_one({"name": "vovkt"})
        _id = result.inserted_id

        actual = await model.read_one({"_id": str(_id)}, strict=False)
        self.assertIsNone(actual)

    async def test_read_by_field(self):
        model = Model(self.db, collection_name="users")
        result = await model.collection.insert_one({"name": "vovkt"})
        _id = result.inserted_id

        actual = await model.read_one({"name": "vovkt"})
        self.assertEqual({"_id": _id, "name": "vovkt"}, actual)