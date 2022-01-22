import typing as t

import pydantic
import pydantic.main
import pydantic.class_validators


class ModelMetaclass(type):
    def __new__(mcs, name, bases, attrs: t.Dict[str, t.Any]):
        pydantic_fields = mcs.get_fields_for_pydantic(attrs)
        pydantic_fields["__annotations__"] = mcs.get_annotations_for_pydantic(attrs)
        mcs.create_model(name, bases, attrs, pydantic_fields)

        attrs.setdefault("__instance__", None)
        cls = super().__new__(mcs, name, bases, attrs)

        return cls

    @classmethod
    def get_annotations_for_pydantic(
        mcs, attrs: t.Dict[str, t.Any]
    ) -> t.Dict[str, t.Any]:
        annotations = attrs.get("__annotations__", {})
        result = {}
        for key in list(annotations):
            if not key.startswith("__"):
                result[key] = annotations.pop(key)
        return result

    @classmethod
    def get_fields_for_pydantic(mcs, attrs: t.Dict[str, t.Any]) -> t.Dict[str, t.Any]:
        result = {}
        for name in list(attrs):
            value = attrs[name]

            if hasattr(value, pydantic.class_validators.ROOT_VALIDATOR_CONFIG_KEY):
                result[name] = attrs.pop(name)
            elif hasattr(value, pydantic.class_validators.VALIDATOR_CONFIG_KEY):
                result[name] = attrs.pop(name)
            elif name == "Config":
                result[name] = attrs.pop(name)
            elif name.startswith("__") or callable(value):
                continue
            else:
                result[name] = value

        return result

    @classmethod
    def get_base_model(mcs, bases, attrs) -> t.Type[pydantic.main.BaseModel]:
        attr = "__model__"
        if attrs.get(attr):
            return attrs[attr]

        for cls in bases:
            if base_model := getattr(cls, attr):
                return base_model

        raise RuntimeError("Attr __model__ not found")

    @classmethod
    def create_model(mcs, name: str, bases, attrs: t.Dict[str, t.Any], fields) -> None:
        """
        Create pydantic model

        pydantic.main.create_model not working with annotations
        """
        model = type(
            name,
            (mcs.get_base_model(bases, attrs),),
            fields,
        )

        attrs["__model__"] = model


class Model(metaclass=ModelMetaclass):
    __model__: t.ClassVar[t.Type[pydantic.main.BaseModel]] = pydantic.main.BaseModel
    """Data storage schema"""
    __instance__: pydantic.main.BaseModel
    """Data storage"""

    id: str = pydantic.Field(default=None, alias="_id")

    class Config:
        validate_assignment = True

    def __init__(self, **kwargs) -> None:
        self.__instance__ = self.__model__(**kwargs)

    def __str__(self) -> str:
        return str(self.__instance__)

    def __repr__(self) -> str:
        return repr(self.__instance__)

    def __getattr__(self, item: str) -> t.Any:
        try:
            return getattr(self.__instance__, item)
        except AttributeError:
            return super().__getattribute__(item)

    def __setattr__(self, name: str, value: t.Any) -> None:
        try:
            object.__getattribute__(self, name)
            super().__setattr__(name, value)
        except AttributeError:
            setattr(self.__instance__, name, value)

    def __eq__(self, o: object) -> bool:
        if isinstance(o, Model):
            return self.__instance__ == o.__instance__
        elif isinstance(o, pydantic.main.BaseModel):
            return self.__instance__ == o
        return super().__eq__(o)

    def __ne__(self, o: object) -> bool:
        if isinstance(o, Model):
            return self.__instance__ != o.__instance__
        elif isinstance(o, pydantic.main.BaseModel):
            return self.__instance__ != o
        return super().__ne__(o)

    def json(self, *args, **kwargs):
        return self.__instance__.json(*args, **kwargs)
