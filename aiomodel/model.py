import typing as t

from bson import ObjectId
from motor.core import AgnosticDatabase, AgnosticCollection
from pymongo.errors import DuplicateKeyError
from pymongo.collection import ReturnDocument

from .types import Document, Projection, RawDocument, Query
from .cursor import WrappedCursor


__all__ = ["Model"]


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
