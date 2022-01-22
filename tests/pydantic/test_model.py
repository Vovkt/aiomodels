from unittest import TestCase
from pydantic import validator, root_validator, Field, BaseModel

from aiomodels.pydantic.model import Model


class TestModel(TestCase):
    def test_default(self):
        class Model1(Model):
            a: str
            b: str = None
            c: str = Field(default_factory=lambda: "c")
            d: str = Field("d")

            @root_validator(pre=True)
            def root_val(cls, values):
                return values

            @validator("a")
            def a_val(cls, v):
                return v

            def method1(self):
                pass

        class Schema1(BaseModel):
            id: str = Field(default=None, alias="_id")
            a: str
            b: str = None
            c: str = Field(default_factory=lambda: "c")
            d: str = Field("d")

            @root_validator(pre=True)
            def root_val(cls, values):
                return values

            @validator("a")
            def a_val(cls, v):
                return v

        actual = Model1.__model__.schema()
        expected = {
            **Schema1.schema(),
            'title': "Model1",
        }

        self.assertEqual(actual, expected)
