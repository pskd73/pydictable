import json
from collections import OrderedDict
from datetime import datetime
from typing import List
from unittest import TestCase

from dictable.core import DictAble, StrField, IntField, ObjectField, ListField, DatetimeField


class TestCore(TestCase):
    def __assert_json_equal(self, json_1, json_2):
        self.assertEqual(json.dumps(json_1), json.dumps(json_2))

    def test_basic(self):
        class Address(DictAble):
            pin_code: int = IntField()
            street: str = StrField()
        input_dict = {'pin_code': 560032, 'street': 'RT Nagar'}
        address = Address(dict=input_dict)
        self.assertEqual(address.pin_code, 560032)
        self.assertEqual(address.street, 'RT Nagar')
        self.assertDictEqual(address.to_json(), input_dict)

    def test_list(self):
        class MessageBox(DictAble):
            messages: List[int] = ListField(IntField())

        input_dict = {'messages': [1, 2, 3, 4]}
        box = MessageBox(dict=input_dict)
        self.assertEqual(len(box.messages), 4)
        self.assertEqual(min(box.messages), 1)
        self.assertDictEqual(box.to_json(), input_dict)

        class Message(DictAble):
            message: str = StrField()

        class MessageBox(DictAble):
            messages: List[Message] = ListField(ObjectField(Message))

        box = MessageBox(dict={'messages': []})
        self.assertEqual(box.messages, [])
        box = MessageBox(dict={'messages': [
            {'message': 'Hello!'}
        ]})
        self.assertEqual(len(box.messages), 1)
        self.assertEqual(box.messages[0].message, 'Hello!')

    def test_object(self):
        class LatLng(DictAble):
            lat: int = IntField()
            lng: int = IntField()

        class Address(DictAble):
            pin_code: int = IntField()
            lat_lng: LatLng = ObjectField(LatLng)

        class Person(DictAble):
            name: str = StrField()
            address: Address = ObjectField(Address)

        input_dict = {
            'name': 'Pramod',
            'address': {
                'pin_code': 560032,
                'lat_lng': {
                    'lat': 12345,
                    'lng': 67890
                }
            }
        }
        p = Person(dict=input_dict)
        self.assertEqual(p.address.lat_lng.lat, 12345)
        self.assertEqual(p.address.pin_code, 560032)
        self.assertDictEqual(p.to_json(), input_dict)

    def test_default(self):
        class Address(DictAble):
            pin_code: int = IntField()

        class Person(DictAble):
            name: str = StrField()
            address: Address = ObjectField(Address)

        p = Person()
        self.assertEqual(p.name, None)
        self.assertEqual(p.address, None)

        p = Person(dict={'address': {}, 'name': 'Pramod'})
        self.assertTrue(p.address is not None)
        self.assertEqual(p.address.pin_code, None)
        self.assertEqual(p.name, 'Pramod')

    def test_init_with_kwargs(self):
        class Address(DictAble):
            pin_code: int = IntField()

        a = Address(pin_code=518466)
        self.assertEqual(a.pin_code, 518466)

    def test_datetime_field(self):
        class Address(DictAble):
            pin_code: int = IntField()
            created_at: datetime = DatetimeField()

        a = Address()
        a.created_at = datetime(2021, 3, 31)
        self.assertEqual(a.to_json()['created_at'], 1617129000000)

        a = Address(dict={'created_at': 1617129000000})
        self.assertEqual(a.created_at, datetime(2021, 3, 31))

    def test_inheritance(self):
        class LivingOrgan(DictAble):
            no_of_hearts: int = IntField()

        class Human(LivingOrgan):
            hand_size: int = IntField()

        h = Human(dict={'no_of_hearts': 1, 'hand_size': 30})
        self.assertEqual(h.no_of_hearts, 1)
        self.assertEqual(h.hand_size, 30)

    def test_init_with_actual_data(self):
        class Address(DictAble):
            pin_code: int = IntField()
            created_at: datetime = DatetimeField()

        a = Address(pin_code=560032, created_at=datetime(2021, 3, 31))
        self.assertEqual(a.to_json()['created_at'], 1617129000000)
