from unittest import TestCase
from pydantic import validator, root_validator

from aiomodels.pydantic.model import Model


class TestModel(TestCase):
    def test_default(self):

        class User(Model):
            name: str

            @root_validator(pre=True)
            def a(self, values):
                return values

            @validator("name")
            def b(self, v):
                return v

        a = User(name='123')
        print(1, a)



