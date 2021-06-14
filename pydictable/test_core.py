import json
from datetime import datetime
from enum import Enum
from typing import List
from unittest import TestCase

from pydictable.core import DictAble
from pydictable.field import IntField, StrField, ListField, ObjectField, DatetimeField, CustomField, MultiTypeField, \
    EnumField


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
        self.assertDictEqual(address.to_dict(), input_dict)

    def test_list(self):
        class MessageBox(DictAble):
            messages: List[int] = ListField(IntField())

        input_dict = {'messages': [1, 2, 3, 4]}
        box = MessageBox(dict=input_dict)
        self.assertEqual(len(box.messages), 4)
        self.assertEqual(min(box.messages), 1)
        self.assertDictEqual(box.to_dict(), input_dict)

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
        self.assertDictEqual(p.to_dict(), input_dict)

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
        self.assertEqual(a.to_dict()['created_at'], 1617129000000)

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
        self.assertEqual(a.to_dict()['created_at'], 1617129000000)

    def test_custom_field(self):
        class Car(DictAble):
            name: str = StrField()

        class CarA(Car):
            a_field: str = StrField()

        class CarB(Car):
            b_field: str = StrField()

        def make_car(car_dict: dict) -> Car:
            if car_dict['__type'] == 'CarA':
                return CarA(dict=car_dict)
            if car_dict['__type'] == 'CarB':
                return CarB(dict=car_dict)

        class Garage(DictAble):
            cars: List[Car] = ListField(CustomField(make_car, lambda c: c.to_dict()))

        g = Garage(dict={
            'cars': [
                {'__type': 'CarA', 'a_field': 'a field', 'name': 'WagonR'},
                {'__type': 'CarB', 'b_field': 'b field', 'name': 'I20'}
            ]
        })
        self.assertEqual(g.to_dict()['cars'][0]['name'], 'WagonR')
        self.assertEqual(g.to_dict()['cars'][1]['name'], 'I20')

        class Garage(DictAble):
            cars: List[Car] = ListField(MultiTypeField([CarA, CarB]))

        g = Garage(dict={
            'cars': [
                {'__type': 'CarA', 'a_field': 'a field', 'name': 'I10'},
                {'__type': 'CarB', 'b_field': 'b field', 'name': 'Mini'}
            ]
        })
        self.assertEqual(g.to_dict()['cars'][0]['name'], 'I10')
        self.assertEqual(g.to_dict()['cars'][1]['name'], 'Mini')

        g = Garage(
            cars=[
                CarA(name='i20', a_field='some value')
            ]
        )
        self.assertEqual(g.to_dict()['cars'][0]['__type'], 'CarA')

    def test_optional(self):
        class Car(DictAble):
            name: str = StrField(required=True)

        self.assertRaises(ValueError, lambda: Car(dict={'name': None}))
        self.assertRaises(ValueError, lambda: Car(dict={}))
        self.assertRaises(ValueError, lambda: Car(name=None))
        self.assertRaises(ValueError, lambda: Car())
        Car(dict={'name': 'Pramod'})

        class Car(DictAble):
            no_of_gears: int = IntField(required=True)
        try:
            Car()
        except ValueError as e:
            self.assertTrue('no_of_gears' in str(e))

    def test_custom_attr(self):
        d = {
            '_id': 1,
            'person_name': 'Pramod'
        }

        class Person(DictAble):
            id: int = IntField(required=True, key='_id')
            name: str = StrField(required=True, key='person_name')

        p = Person(dict=d)
        self.assertEqual(p.name, 'Pramod')
        self.assertEqual(p.id, 1)
        d = p.to_dict()
        self.assertEqual(d['_id'], 1)
        self.assertEqual(d['person_name'], 'Pramod')

    def test_support_enum(self):
        class EmployeeType(Enum):
            ADMIN = 'ADMIN'
            MANAGER = 'MANAGER'
            DEV = 2

        d = {
            'emp_id': 23,
            'type': 'ADMIN',
            'roles': ['ADMIN', 'MANAGER', 2]
        }

        class Employee(DictAble):
            id: int = IntField(required=True, key='emp_id')
            type: EmployeeType = EnumField(EmployeeType)
            roles: List[EmployeeType] = ListField(EnumField(EmployeeType))

        e = Employee(dict=d)
        self.assertEqual(e.type, EmployeeType.ADMIN)
        d = e.to_dict()
        self.assertEqual(d['type'], 'ADMIN')
        self.assertEqual(e.roles, [EmployeeType.ADMIN, EmployeeType.MANAGER, EmployeeType.DEV])
        d = e.to_dict()
        self.assertEqual(d['roles'], ['ADMIN', 'MANAGER', 2])
        d = {
            'emp_id': 23,
            'type': 'ADMIN',
            'roles': ['ADMIN', 'MANAGER', 4]
        }
        self.assertRaises(ValueError, lambda: Employee(dict=d))

    def test_datetime(self):
        class User(DictAble):
            date: datetime = DatetimeField(required=True)

        self.assertRaises(ValueError, lambda: User(date=None))

    def test_wrong_type(self):
        class User(DictAble):
            num: int = IntField(required=True)

        self.assertRaises(ValueError, lambda: User(dict={'num': '1'}))
        self.assertRaises(ValueError, lambda: User(dict={'num': None}))
        u = User(dict={'num': 1})
        self.assertEqual(1, u.num)
