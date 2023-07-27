from unittest import TestCase

from pydictable import DictField, StrField, DataValidationError, DictAble, ObjectField, IntField, RangeIntField


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

        class School(DictAble):
            name: str
            students = DictField()

        spec = School.get_input_spec()
        self.assertEqual(spec['students']['of']['key']['type'], 'AnyField')
        self.assertEqual(spec['students']['of']['value']['type'], 'AnyField')

    def test_custom_dict_spec(self):
        class CustomTextField(StrField):
            def __init__(self, label: str = None, regex: str = None):
                super().__init__()
                self.label = label
                self.regex = regex

        class CustomIntNumberField(IntField):
            def __init__(self, label: str = None, min_length: int = None, max_length: int = None):
                super().__init__()
                self.label = label
                self.min_length = min_length
                self.max_length = max_length

        class CustomSpecSchema(DictAble):
            name: str = CustomTextField(label='User name', regex='r')
            mobile: int = CustomIntNumberField(label='Mobile no', max_length=11, min_length=10)
            age: int = RangeIntField(max_val=30, min_val=18)

        self.assertEqual(
            CustomSpecSchema.get_custom_input_spec(),
            {
                'age': {
                    'type': 'RangeIntField', 'required': False, 'of': {'min': 18, 'max': 30}, 'key': None,
                    'default': None, 'default_factory': None, 'min_val': 18, 'max_val': 30
                },
                'mobile': {
                    'type': 'CustomIntNumberField', 'required': False, 'key': None, 'default': None,
                    'default_factory': None, 'label': None, 'min_length': 10, 'max_length': 11
                },
                'name': {
                    'type': 'CustomTextField', 'required': False, 'key': None, 'default': None,
                    'default_factory': None, 'label': 'User name', 'regex': 'r'
                }
            }
        )


