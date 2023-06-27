from unittest import TestCase

from pydictable import DictField, StrField, DataValidationError, DictAble, ObjectField


class TestField(TestCase):
    def test_dict_key_value(self):
        field = DictField(StrField(required=True), StrField(required=True))
        self.assertRaises(AssertionError, lambda: field.validate_dict('x', 'hi'))
        self.assertRaises(AssertionError, lambda: field.validate_dict('x', 1))
        field.validate_dict('x', {})
        field.validate_dict('x', {'name': 'pramod'})

        self.assertRaises(DataValidationError, lambda: field.validate_dict('x', {'name': 1}))
        self.assertRaises(DataValidationError, lambda: field.validate_dict('x', {1: 'hello'}))

        class Person(DictAble):
            age: int

        field = DictField(StrField(required=True), ObjectField(Person, required=True))
        self.assertRaises(AssertionError, lambda: field.validate_dict('x', 'hello'))

        field.validate_dict('x', {'pramod': {'age': 2}})
        self.assertEqual(field.from_dict({'pramod': {'age': 2}})['pramod'].age, 2)

    def test_dict_spec(self):
        class Student(DictAble):
            name: str

        class School(DictAble):
            name: str
            students = DictField(key_type=StrField(), value_type=ObjectField(Student))

        spec = School.get_input_spec()
        self.assertEqual(spec['name']['type'], 'StrField')
        self.assertEqual(spec['students']['type'], 'DictField')
        self.assertEqual(spec['students']['of']['key']['type'], 'StrField')
        self.assertEqual(spec['students']['of']['value']['type'], 'ObjectField')
        self.assertEqual(spec['students']['of']['value']['of']['name']['type'], 'StrField')
