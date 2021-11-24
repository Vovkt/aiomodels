from bson import ObjectId

from pymongo.errors import DuplicateKeyError

from aiomodels.core import WrappedCursor, BaseModel
from aiomodels.testing import BaseTestModel


class TestModelGenerateId(BaseTestModel):
    def test_default(self):
        model: BaseModel = BaseModel(self.db, collection_name="users")
        _id = model.generate_id()
        self.assertIsInstance(_id, ObjectId)


class TestModelCreate(BaseTestModel):
    async def test_default(self):
        model = BaseModel(self.db, collection_name="users")
        doc = await model.create_one({"name": "Vovkt"})

        collection = model.collection
        actual = await collection.find_one(doc["_id"])
        self.assertEqual(doc, actual)

    async def test_duplicate_exception(self):
        model = BaseModel(self.db, collection_name="users")
        collection = model.collection

        await collection.create_index("name", unique=True)

        await model.create_one({"name": "Vovkt"})
        with self.assertRaises(DuplicateKeyError):  # todo check context
            await model.create_one({"name": "Vovkt"})


class TestModelRead(BaseTestModel):
    async def test_empty(self):
        model = BaseModel(self.db, collection_name="users")
        result = await model.collection.insert_one({"name": "Vovkt"})
        _id = result.inserted_id

        actual = await model.read_one()
        self.assertEqual({"_id": _id, "name": "Vovkt"}, actual)

    async def test_by_object_id(self):
        model = BaseModel(self.db, collection_name="users")
        result = await model.collection.insert_one({"name": "Vovkt"})
        _id = result.inserted_id

        actual = await model.read_one(_id)
        self.assertEqual({"_id": _id, "name": "Vovkt"}, actual)

    async def test_by_string_instead_object_id(self):
        model = BaseModel(self.db, collection_name="users")
        result = await model.collection.insert_one({"name": "Vovkt"})
        _id = result.inserted_id

        actual = await model.read_one(str(_id), strict=False)
        self.assertIsNone(actual)

    async def test_by_query_by_object_id(self):
        model = BaseModel(self.db, collection_name="users")
        result = await model.collection.insert_one({"name": "Vovkt"})
        _id = result.inserted_id

        actual = await model.read_one({"_id": _id})
        self.assertEqual({"_id": _id, "name": "Vovkt"}, actual)

    async def test_by_query_by_string(self):
        model = BaseModel(self.db, collection_name="users")
        result = await model.collection.insert_one({"name": "Vovkt"})
        _id = result.inserted_id

        actual = await model.read_one({"_id": str(_id)}, strict=False)
        self.assertIsNone(actual)

    async def test_by_field(self):
        model = BaseModel(self.db, collection_name="users")
        result = await model.collection.insert_one({"name": "Vovkt"})
        _id = result.inserted_id

        actual = await model.read_one({"name": "Vovkt"})
        self.assertEqual({"_id": _id, "name": "Vovkt"}, actual)

    async def test_not_found(self):
        model = BaseModel(self.db, collection_name="users")

        with self.assertRaises(Exception):  # todo
            await model.read_one({})


class TestModelReadMany(BaseTestModel):
    async def test_default(self):
        model = BaseModel(self.db, collection_name="users")
        cursor = model.read_many()

        self.assertIsInstance(cursor, WrappedCursor)


class TestModelUpdate(BaseTestModel):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()
        self.model = BaseModel(self.db, collection_name="users")

    async def test_default(self):
        user_1 = await self.model.create_one({"name": "Vovkt"})
        actual = await self.model.update_one(
            {"_id": user_1["_id"]}, {"$set": {"name": "Vladimir"}}
        )

        self.assertEqual(
            {
                "_id": user_1["_id"],
                "name": "Vladimir",
            },
            actual,
        )

    async def test_upsert_new(self):
        user_1 = await self.model.update_one(
            {"name": "Vovkt"}, {"$set": {"name": "Natasyan"}}, upsert={}
        )
        actual = await self.model.read_one({"_id": user_1["_id"]})

        self.assertEqual(user_1, actual)

    async def test_upsert_new_with_id(self):
        _id = ObjectId()
        user_1 = await self.model.update_one(
            {"name": "Vovkt"},
            {"$set": {"name": "Natasyan"}},
            upsert={
                "_id": _id,
            },
        )
        actual = await self.model.read_one({"_id": _id})

        self.assertEqual(
            user_1,
            actual,
        )
