from aiomodels import Model
from aiomodels.testing import BaseTestModel


class TestCursorWrapper(BaseTestModel):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()
        self.model = Model(self.db, collection_name="users")

    async def test_await(self):
        user_1 = await self.model.create_one({"name": "vovkt"})
        user_2 = await self.model.create_one({"name": "natasyan"})
        user_3 = await self.model.create_one({"name": "mini"})

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
        user_1 = await self.model.create_one({"name": "vovkt"})
        user_2 = await self.model.create_one({"name": "natasyan"})
        user_3 = await self.model.create_one({"name": "mini"})

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
        user_1 = await self.model.create_one({"name": "vovkt"})
        user_2 = await self.model.create_one({"name": "natasyan"})
        user_3 = await self.model.create_one({"name": "mini"})

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
        user_1 = await self.model.create_one({"name": "vovkt"})
        user_2 = await self.model.create_one({"name": "natasyan"})
        user_3 = await self.model.create_one({"name": "mini"})

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
        user_1 = await self.model.create_one({"name": "vovkt"})
        user_2 = await self.model.create_one({"name": "natasyan"})
        user_3 = await self.model.create_one({"name": "mini"})
        user_4 = await self.model.create_one({"name": "anon"})

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
