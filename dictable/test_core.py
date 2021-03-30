from typing import List
from unittest import TestCase

from dictable.core import DictAble, StrField, IntField, ObjectField, ListField


class TestCore(TestCase):
    def test_basic(self):
        class Address(DictAble):
            pin_code: int = IntField()
            street: str = StrField()
        address = Address({'pin_code': 560032, 'street': 'RT Nagar'})
        self.assertEqual(address.pin_code, 560032)
        self.assertEqual(address.street, 'RT Nagar')

    def test_list(self):
        class MessageBox(DictAble):
            messages: List[int] = ListField(IntField())

        box = MessageBox({'messages': [1, 2, 3, 4]})
        self.assertEqual(len(box.messages), 4)
        self.assertEqual(min(box.messages), 1)

        class Message(DictAble):
            message: str = StrField()

        class MessageBox(DictAble):
            messages: List[Message] = ListField(ObjectField(Message))

        box = MessageBox({'messages': []})
        self.assertEqual(box.messages, [])
        box = MessageBox({'messages': [
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

        p = Person({
            'name': 'Pramod',
            'address': {
                'pin_code': 560032,
                'lat_lng': {
                    'lat': 12345,
                    'lng': 67890
                }
            }
        })
        self.assertEqual(p.address.lat_lng.lat, 12345)
        self.assertEqual(p.address.pin_code, 560032)
