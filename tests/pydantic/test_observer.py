from unittest import TestCase

from aiomodels.pydantic.observer import create_observer


class TestDictObserver(TestCase):
    def test_update_args(self):
        storage = create_observer({})
        self.assertFalse(storage.modified)
        storage.update({"a": 1})
        self.assertTrue(storage.modified)
        self.assertEqual(
            storage,
            {
                "a": 1,
            },
        )

    def test_update_kwargs(self):
        storage = create_observer({})
        self.assertFalse(storage.modified)
        storage.update(a=1)
        self.assertTrue(storage.modified)
        self.assertEqual(
            storage,
            {
                "a": 1,
            },
        )

    def test_clear(self):
        storage = create_observer({"a": 1})
        self.assertFalse(storage.modified)
        storage.clear()
        self.assertTrue(storage.modified)

        self.assertEqual(storage, {})

    def test_copy(self):
        storage = create_observer({"a": 1})

        copy = {**storage}
        copy["b"] = 1

        self.assertFalse(storage.modified)
        self.assertEqual(storage, {"a": 1})
        self.assertEqual(copy, {"a": 1, "b": 1})

    def test_copy_inner(self):
        storage = create_observer({"a": {"b": 1}})

        copy = {**storage}
        copy["a"]["c"] = 2

        self.assertTrue(storage.modified)
        self.assertEqual(copy, {"a": {"b": 1, "c": 2}})
