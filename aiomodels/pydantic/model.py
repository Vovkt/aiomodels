import typing as t
import pydantic.main

from aiomodels import base, core


class ModelMetaclass(type):

    def __new__(mcls, name, bases, attrs):
        fields = {
            key: (value, ...)
            for key, value in (attrs.get("__annotations__") or {}).items()
        }
        model = pydantic.main.create_model(
            name,
            **fields
        )
        attrs['__annotations__'] = {}
        attrs["_model"] = model

        cls = super().__new__(mcls, name, bases, attrs)

        print(cls)
        print('\t', name)
        print('\t', bases)
        print('\t', attrs)
        print('\t', model)

        return cls

class Model(metaclass=ModelMetaclass):

    def __init__(self, *args, **kwargs) -> None:
        self._instance: pydantic.main.BaseModel = self._model(*args, **kwargs)

    def __str__(self):
        return self._instance.__str__()

    def __repr__(self):
        return self._instance.__repr__()
