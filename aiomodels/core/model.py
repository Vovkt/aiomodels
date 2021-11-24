import asyncio
import typing as t

from bson import ObjectId
from motor.core import AgnosticDatabase, AgnosticCollection
from pymongo.errors import DuplicateKeyError
from pymongo.collection import ReturnDocument

from aiomodels.base import Projection, Query
from aiomodels.core.cursor import WrappedCursor


__all__ = ["BaseModel"]


T = t.TypeVar("T")
P = t.TypeVar("P")


class BaseModel(t.Generic[T, P]):
    db: AgnosticDatabase
    collection_name: str
    collection: AgnosticCollection

    def __init__(self, db: AgnosticDatabase, collection_name: str):
        self.db = db
        self.collection_name = collection_name
        self.collection = db[self.collection_name]

    @staticmethod
    def generate_id() -> P:
        return ObjectId()

    ##
    # Create
    #
    async def _before_create(self, new: T) -> dict:
        document = t.cast(dict, new)
        document.setdefault("_id", self.generate_id())
        return document

    async def _after_create(self, document: dict) -> T:
        return t.cast(T, document)

    async def create_one(self, new: T) -> T:
        document: dict = await self._before_create(new)
        try:
            await self.collection.insert_one(document)
        except DuplicateKeyError:
            raise  # todo
        return await self._after_create(document)

    ##
    # Read
    #
    async def _after_read(self, document: dict) -> T:
        return t.cast(T, document)

    async def read_one(
        self,
        query: t.Union[ObjectId, str, Query] = None,
        *,
        projection: Projection = None,
        strict: bool = True,
    ) -> t.Optional[T]:  # todo upsert
        doc = await self.collection.find_one(filter=query, projection=projection)
        if doc is not None:
            return await self._after_read(doc)
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
    async def _before_update(
        self, query: Query, update: dict, upsert: dict = None, sort=None
    ):
        if upsert is not None:
            document: dict = update.setdefault("$setOnInsert", upsert)
            document.setdefault("_id", self.generate_id())
        return {
            "filter": query,
            "update": update,
            "return_document": ReturnDocument.AFTER,
            "upsert": "$setOnInsert" in update,
            "sort": sort,
        }

    async def _after_update(
        self, document: dict, *, update: dict, upsert: bool, **kwargs
    ) -> T:
        return t.cast(T, document)

    async def update_one(
        self,
        query: Query,
        update: dict,
        *,
        sort=None,
        upsert: dict = None,
        session=None,
        projection: Projection = None,
        strict: bool = True,
    ) -> t.Optional[T]:
        # todo session
        kwargs = await self._before_update(
            query=query, update=update, upsert=upsert, sort=sort
        )

        try:
            document = await self.collection.find_one_and_update(
                **kwargs,
                projection=projection,
                session=session,
            )
        except DuplicateKeyError:
            raise  # todo
        # todo pymongo.errors.OperationFailure: Updating the path 'name' would create a conflict at 'name', full error: {'ok': 0.0, 'errmsg': "Updating the path 'name' would create a conflict at 'name'", 'code': 40, 'codeName': 'ConflictingUpdateOperators'}

        if document is not None:
            return await self._after_update(document, **kwargs)
        elif strict:
            raise Exception("not found")

        return None

    async def update_many(self, query: Query, update: dict) -> int:
        aws = [
            self.update_one({"_id": doc["_id"]}, update)
            async for doc in self.read_many(filter=query, projection={"_id": True})
        ]
        result = await asyncio.gather(*aws)
        return len(result)

    ##
    # Delete
    #
    async def _before_delete(self, query: Query) -> Query:
        return query

    async def _after_delete(self, document: dict) -> T:
        return t.cast(T, document)

    async def delete_one(
        self,
        query: Query,
        *,
        sort=None,
        projection: Projection = None,
        strict: bool = True,
    ) -> t.Optional[T]:
        query = await self._before_delete(query)
        document = await self.collection.find_one_and_delete(
            query, sort=sort, projection=projection
        )
        if document is not None:
            return await self._after_delete(document)
        elif strict:
            raise Exception("not found")
        return None

    async def delete_many(
        self, query: Query, *, projection: Projection = None
    ) -> t.List[T]:
        aws = [
            self.delete_one({"_id": doc["_id"]}, projection=projection)
            async for doc in self.read_many(query, projection={"_id": True})
        ]
        return await asyncio.gather(*aws)
