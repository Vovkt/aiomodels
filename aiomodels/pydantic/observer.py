import typing as t
import collections

T = t.TypeVar("T")


class Observer(t.Generic[T]):
    __slots__ = ("modified", "data", "parent")

    def __init__(self, data: T, parent: "Observer" = None):
        self.data: T = data
        self.parent: t.Optional[Observer] = parent
        self.modified = False

    def __str__(self):
        return str(self.data)

    def __repr__(self):
        return repr(self.data)

    def __dir__(self) -> t.Iterable[str]:
        return dir(self.data)

    def __hash__(self):
        return hash(self.data)

    def __eq__(self, other):
        return self.data == other

    def __ne__(self, other):
        return self.data != other

    def __copy__(self):
        return self.data.__copy__()

    def set_modified(self):
        if self.parent:
            self.parent.set_modified()
        self.modified = True


class DictObserver(Observer[t.Dict], collections.MutableMapping):
    def __getitem__(self, k):
        item = self.data.__getitem__(k)
        if not self.modified:
            return create_observer(item, parent=self)
        return item

    def __setitem__(self, k, v) -> None:
        self.set_modified()
        return self.data.__setitem__(k, v)

    def __delitem__(self, v) -> None:
        self.set_modified()
        return self.data.__delitem__(v)

    def __len__(self) -> int:
        return self.data.__len__()

    def __iter__(self) -> t.Iterator:
        return self.data.__iter__()

    def update(self, *args, **kwargs) -> None:
        self.set_modified()
        self.data.update(*args, **kwargs)

    def clear(self) -> None:
        self.set_modified()
        self.data.clear()

    def pop(self, *args, **kwargs) -> t.Any:
        self.set_modified()
        return self.data.pop(*args, **kwargs)

    def popitem(self):
        self.set_modified()
        return self.data.popitem()

    def setdefault(self, *args, **kwargs):
        self.set_modified()
        return self.data.setdefault(*args, **kwargs)


def create_observer(
    item: t.Union[t.Dict, t.Any], parent=None
) -> t.Union[Observer, t.Any]:
    if isinstance(item, dict):
        return DictObserver(item, parent=parent)
    return item
