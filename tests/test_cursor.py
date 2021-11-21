from aiomodels import Model
from aiomodels.testing import BaseTestModel


class TestCursorWrapper(BaseTestModel):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()
        self.model = Model(self.db, collection_name="users")

    async def test_await(self):
        user_1 = await self.model.create_one({"name": "Vovkt"})
        user_2 = await self.model.create_one({"name": "Natasyan"})
        user_3 = await self.model.create_one({"name": "Mini"})

        cursor = self.model.read_many()

        self.assertEqual(
            await cursor,
            [
                user_1,
                user_2,
                user_3,
            ],
        )

    async def test_iterator(self):
        user_1 = await self.model.create_one({"name": "Vovkt"})
        user_2 = await self.model.create_one({"name": "Natasyan"})
        user_3 = await self.model.create_one({"name": "Mini"})

        cursor = self.model.read_many()

        result = [item async for item in cursor]

        self.assertEqual(
            result,
            [
                user_1,
                user_2,
                user_3,
            ],
        )

    async def test_to_list_default(self):
        user_1 = await self.model.create_one({"name": "Vovkt"})
        user_2 = await self.model.create_one({"name": "Natasyan"})
        user_3 = await self.model.create_one({"name": "Mini"})

        cursor = self.model.read_many()

        result = await cursor.to_list()

        self.assertEqual(
            result,
            [
                user_1,
                user_2,
                user_3,
            ],
        )

    async def test_to_list_with_none(self):
        user_1 = await self.model.create_one({"name": "Vovkt"})
        user_2 = await self.model.create_one({"name": "Natasyan"})
        user_3 = await self.model.create_one({"name": "Mini"})

        cursor = self.model.read_many()

        result = await cursor.to_list(length=None)

        self.assertEqual(
            result,
            [
                user_1,
                user_2,
                user_3,
            ],
        )

    async def test_to_list_with_length(self):
        user_1 = await self.model.create_one({"name": "Vovkt"})
        user_2 = await self.model.create_one({"name": "Natasyan"})
        user_3 = await self.model.create_one({"name": "Mini"})
        user_4 = await self.model.create_one({"name": "Anon"})

        cursor = self.model.read_many()

        result = await cursor.to_list(length=1)
        self.assertEqual(
            result,
            [
                user_1,
            ],
        )

        result = await cursor.to_list(length=2)
        self.assertEqual(
            result,
            [
                user_2,
                user_3,
            ],
        )

        result = await cursor.to_list(length=1)
        self.assertEqual(
            result,
            [
                user_4,
            ],
        )

        result = await cursor.to_list(length=1)
        self.assertEqual(result, [])

        result = await cursor.to_list()
        self.assertEqual(result, [])

    async def test_sort_args(self):
        user_1 = await self.model.create_one({"name": "Vovkt"})
        user_2 = await self.model.create_one({"name": "Natasyan"})
        user_3 = await self.model.create_one({"name": "Mini"})

        result = await self.model.read_many().sort("_id", -1)
        self.assertEqual(result, [user_3, user_2, user_1])

    async def test_sort_with_array(self):
        user_1 = await self.model.create_one({"name": "Vovkt"})
        user_2 = await self.model.create_one({"name": "Natasyan"})
        user_3 = await self.model.create_one({"name": "Mini"})

        result = await self.model.read_many().sort([("_id", -1)])
        self.assertEqual(result, [user_3, user_2, user_1])

    async def test_sort_two_fields(self):
        user_1 = await self.model.create_one({"name": "aaa", "level": 2})
        user_2 = await self.model.create_one({"name": "bbb", "level": 2})
        user_3 = await self.model.create_one({"name": "ccc", "level": 1})

        result = await self.model.read_many().sort([("level", -1), ("name", -1)])

        self.assertEqual(result, [user_2, user_1, user_3])
