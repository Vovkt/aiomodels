import asyncio
import typing as t

from pymongo.errors import DuplicateKeyError
from pymongo.collection import ReturnDocument
from bson import ObjectId
from motor.core import AgnosticDatabase, AgnosticCollection, AgnosticCursor
from motor.motor_asyncio import AsyncIOMotorClient

Projection = t.Dict[str, bool]
Query = t.Dict[str, t.Any]
RawDocument = t.Dict[str, t.Any]
Document = t.Dict[str, t.Any]


class WrappedCursor:
    def __init__(
        self, model: "Model", *, cursor: AgnosticCursor = None, **kwargs
    ) -> None:
        self.model: "Model" = model
        self.cursor: AgnosticCursor = cursor or self.model.collection.find(**kwargs)

    def __aiter__(self) -> "WrappedCursor":
        return self

    async def __anext__(self) -> RawDocument:
        return await self.model.after_read(await self.cursor.next())

    def __await__(self):
        # todo types?
        return self.to_list().__await__()

    async def to_list(self, length: int = None) -> t.List[RawDocument]:
        # todo gather?
        return [
            await self.model.after_read(doc)
            for doc in await self.cursor.to_list(length)
        ]

    ##
    # Cursor operations
    #
    def clone(self, cursor: AgnosticCursor = None) -> "WrappedCursor":
        return self.__class__(self.model, cursor=cursor or self.cursor.clone())

    def sort(self, *args, **kwargs) -> "WrappedCursor":
        return self.clone(cursor=self.cursor.sort(*args, **kwargs))

    def skip(self, offset: int) -> "WrappedCursor":
        return self.clone(cursor=self.cursor.skip(offset))

    def limit(self, limit: int) -> "WrappedCursor":
        return self.clone(cursor=self.cursor.limit(limit))


class Model:
    db: AgnosticDatabase
    collection_name: str
    collection: AgnosticCollection

    def __init__(self, db: AgnosticDatabase, collection_name: str):
        self.db = db
        self.collection_name = collection_name
        self.collection = db[self.collection_name]

    @staticmethod
    def generate_id():
        return ObjectId()

    ##
    # Create
    #
    async def before_create(self, document: Document) -> RawDocument:
        return {
            "_id": self.generate_id(),
            **document,
        }

    async def after_create(self, document: RawDocument) -> Document:
        return document

    async def create_one(self, document: Document) -> Document:
        doc: RawDocument = await self.before_create(document)
        try:
            await self.collection.insert_one(doc)
        except DuplicateKeyError:
            raise  # todo
        return await self.after_create(doc)

    ##
    # Read
    #
    async def after_read(self, document: RawDocument) -> Document:
        return document

    async def read_one(
        self,
        query: t.Union[ObjectId, str, Query],
        projection: Projection = None,
        *,
        strict=True,
    ) -> t.Optional[Document]:  # todo upsert
        doc = await self.collection.find_one(filter=query, projection=projection)
        if doc is not None:
            return await self.after_read(doc)
        elif strict:
            raise Exception("not found")
        return None

    def read_many(
        self, query: Query = None, *, projection: Projection = None, **kwargs
    ) -> WrappedCursor:
        return WrappedCursor(
            self,
            filter=query,
            projection=projection,
            **kwargs,
        )

    ##
    # Update
    #
    # todo examples with before
    async def before_update(
        self, query, update: RawDocument, upsert: RawDocument = None, sort=None
    ):
        if upsert is not None:
            document = update.setdefault("$setOnInsert", {})
            document.update(await self.before_create(upsert))
        return {
            "filter": query,
            "update": update,
            "return_document": ReturnDocument.AFTER,
            "upsert": upsert is not None,
            "sort": sort,
        }

    async def after_update(
        self, document: RawDocument, *, update: dict, upsert: bool, **kwargs
    ) -> Document:
        if upsert and update["$setOnInsert"]["_id"] == document["_id"]:
            return await self.after_create(document)
        return await self.after_read(document)

    async def update_one(
        self,
        query: Query,
        update: RawDocument,
        *,
        sort=None,
        upsert: RawDocument = None,
        projection: Projection = None,
        strict: bool = True,
    ) -> t.Optional[Document]:
        # todo session
        kwargs = await self.before_update(
            query=query, update=update, upsert=upsert, sort=sort
        )

        try:
            doc = await self.collection.find_one_and_update(
                **kwargs, projection=projection
            )
        except DuplicateKeyError:
            raise  # todo
        # todo pymongo.errors.OperationFailure: Updating the path 'name' would create a conflict at 'name', full error: {'ok': 0.0, 'errmsg': "Updating the path 'name' would create a conflict at 'name'", 'code': 40, 'codeName': 'ConflictingUpdateOperators'}

        if doc is not None:
            return await self.after_update(doc, **kwargs)
        elif strict:
            raise Exception("not found")

        return None

    async def update_many(self):
        pass

    ##
    # Delete
    #
    async def after_delete(self, document: RawDocument) -> None:
        pass

    async def delete_one(self):
        pass

    async def delete_many(self):
        pass


async def main():
    db = AsyncIOMotorClient("mongodb://localhost/")

    users = Model(db["simple-test"], collection_name="users")

    assert await users.read_one("61928821dc8768385af8772a", strict=False) is None
    assert (
        await users.read_one({"_id": "61928821dc8768385af8772a"}, strict=False) is None
    )
    assert await users.read_one(ObjectId("61928821dc8768385af8772a")) is not None
    assert (
        await users.read_one({"_id": ObjectId("61928821dc8768385af8772a")}) is not None
    )

    b = await users.update_one(
        {"name": "1235121"}, {"$set": {"name": "1235121"}}, upsert={}
    )
    print(b)

    print(await users.read_many())
    print(await users.collection.count_documents({}))
    #
    # async for user in users.read_many():
    #     print(user)
    #     print(await users.read_one(user["_id"]))
    #     print(await users.read_one({"_id": user["_id"]}))


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
