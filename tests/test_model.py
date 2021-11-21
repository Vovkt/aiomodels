from bson import ObjectId

from pymongo.errors import DuplicateKeyError

from aiomodels import WrappedCursor, Model
from aiomodels.testing import BaseTestModel


class TestModelGenerateId(BaseTestModel):
    def test_default(self):
        model: Model = Model(self.db, collection_name="users")
        _id = model.generate_id()
        self.assertIsInstance(_id, ObjectId)


class TestModelCreate(BaseTestModel):
    async def test_default(self):
        model = Model(self.db, collection_name="users")
        doc = await model.create_one({"name": "vovkt"})

        collection = model.collection
        actual = await collection.find_one(doc["_id"])
        self.assertEqual(doc, actual)

    async def test_duplicate_exception(self):
        model = Model(self.db, collection_name="users")
        collection = model.collection

        await collection.create_index("name", unique=True)

        await model.create_one({"name": "vovkt"})
        with self.assertRaises(DuplicateKeyError):  # todo check context
            await model.create_one({"name": "vovkt"})


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


class TestModelReadMany(BaseTestModel):
    async def test_default(self):
        model = Model(self.db, collection_name="users")
        cursor = model.read_many()

        self.assertIsInstance(cursor, WrappedCursor)
