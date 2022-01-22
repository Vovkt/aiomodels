from unittest import TestCase

from pydantic import validator, root_validator, Field, BaseModel, ValidationError

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
            "title": "Model1",
        }

        self.assertEqual(actual, expected)

    def test_eq(self):
        class ModelEq(Model):
            name: str

        user1 = ModelEq(name="Vovkt")
        user2 = ModelEq(name="Vovkt")
        self.assertEqual(user1, user2)

    def test_ne(self):
        class ModelEq(Model):
            name: str

        user1 = ModelEq(name="Vovkt")
        user2 = ModelEq(name="Natasyna")
        self.assertNotEqual(user1, user2)

    def test_validation(self):
        class ModelS(Model):
            val: int

        with self.assertRaises(ValidationError):
            ModelS(val="s")

        b = ModelS(val=1)
        with self.assertRaises(ValidationError):
            b.val = "s"
