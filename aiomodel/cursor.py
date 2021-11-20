import typing as t

from motor.core import AgnosticCursor

from .base import RawDocument

if t.TYPE_CHECKING:
    from .model import Model


__all__ = ["WrappedCursor"]


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
