from enum import Enum
from typing import TypeVar, Generic, List
from unittest import TestCase

from pydictable import GenericDictAble, ListField, EnumField, DictAble, ObjectField, DataValidationError


class TestGeneric(TestCase):
    def test_generic(self):
        class Gender(Enum):
            male = 'male'
            female = 'female'

        class City(Enum):
            Bangalore = 'Bangalore'
            Chennai = 'Chennai'

        T = TypeVar('T')

        class SelectField(GenericDictAble, Generic[T]):
            options: List[T] = None

            @staticmethod
            def inject(item: T):
                return {'options': ListField(EnumField(item))}

        class Profile(DictAble):
            gender: SelectField[Gender] = ObjectField(SelectField.make(Gender))

        class Lead(DictAble):
            city: SelectField[City] = ObjectField(SelectField.make(City))

        p = Profile(dict={'gender': {'options': ['male']}})
        l = Lead(dict={'city': {'options': ['Bangalore']}})
        self.assertEqual(p.gender.options[0], Gender.male)
        self.assertNotEqual(l.city.options[0], Gender.male)
        self.assertEqual(l.city.options[0], City.Bangalore)

        self.assertRaises(DataValidationError, lambda: Profile(dict={'gender': {'options': ['invalid']}}))
