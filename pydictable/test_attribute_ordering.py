from unittest import TestCase

from pydictable import StrField, IntField, FloatField, DictAble


class TestAttributeOrdering(TestCase):

    def test_only_type_hints(self):
        class TestSchema(DictAble):
            delta: str
            charlie: str
            alpha: int
            beta: float

        obj = TestSchema(dict={
            'delta': 'four',
            'charlie': 'one',
            'alpha': 10,
            'beta': 5.3
        })
        self.assertEqual(list(obj.to_dict().keys()), ['delta', 'charlie', 'alpha', 'beta'])

    def test_only_dict_fields(self):
        class TestSchema(DictAble):
            delta: str = StrField(required=True)
            charlie: str = StrField(required=False)
            alpha: int = IntField(required=True)
            beta: float = FloatField(required=False)

        obj = TestSchema(dict={
            'delta': 'four',
            'charlie': 'one',
            'alpha': 10,
            'beta': 5.3
        })
        self.assertEqual(list(obj.to_dict().keys()), ['delta', 'charlie', 'alpha', 'beta'])

    def test_type_hints_and_then_dict_fields(self):

        class TestSchema(DictAble):
            delta: str
            charlie: str = StrField(required=False)
            alpha: int = IntField(required=True)
            beta: float

        obj = TestSchema(dict={
            'delta': 'four',
            'charlie': 'one',
            'alpha': 10,
            'beta': 5.3
        })
        self.assertEqual(list(obj.to_dict().keys()), ['delta', 'charlie', 'alpha', 'beta'])

    def test_dict_fields_and_then_type_hints(self):

        class TestSchema(DictAble):
            delta: str = StrField(required=False)
            charlie: str = StrField(required=False)
            alpha: int
            beta: float

        obj = TestSchema(dict={
            'delta': 'four',
            'charlie': 'one',
            'alpha': 10,
            'beta': 5.3
        })
        self.assertEqual(list(obj.to_dict().keys()), ['delta', 'charlie', 'alpha', 'beta'])

    def test_dict_fields_without_type_hints(self):

        class TestSchema(DictAble):
            delta = StrField(required=False)
            charlie: str = StrField(required=False)
            alpha: int
            beta: float

        obj = TestSchema(dict={
            'delta': 'four',
            'charlie': 'one',
            'alpha': 10,
            'beta': 5.3
        })
        self.assertEqual(list(obj.to_dict().keys()), ['charlie', 'alpha', 'beta', 'delta'])
