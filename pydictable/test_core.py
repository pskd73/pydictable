import json
import math
from datetime import datetime
from enum import Enum
from time import sleep
from typing import List, Dict, Optional, Union, Any
from unittest import TestCase
from pydictable.core import DictAble, partial
from pydictable.field import IntField, StrField, ListField, ObjectField, DatetimeField, CustomField, MultiTypeField, \
    EnumField, DictField, DictValueField, UnionField, DataValidationError, RegexField, RangeIntField, RangeFloatField, \
    NoneField


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

        class Block(DictAble):
            blocks: Optional[list]

        Block(dict={})

        class Block(DictAble):
            blocks: Optional[List[Any]]

        Block(dict={})

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

        class DateMillisField(IntField):
            def validate_dict(self, field_name: str, v):
                super().validate_dict(field_name, v)
                assert len(str(v)) == 13, "Length should be 13"

        class PanField(StrField):
            def validate_dict(self, field_name: str, v):
                super().validate_dict(field_name, v)
                assert len(v) == 10

        class User(DictAble):
            dob: int = DateMillisField(required=True)
            pan: str = PanField(required=True)

        try:
            User(dict={'dob': 3456788, 'pan': 'BKEPS9876L'})
        except DataValidationError as e:
            self.assertEqual(e.err, 'Pre check failed: Length should be 13')

        try:
            User(dict={'dob': 1672724424703, 'pan': 'BKSFER'})
        except DataValidationError as e:
            self.assertEqual(e.err, 'Pre check failed: Invalid value BKSFER for field pan')

    def test_optional(self):
        class Car(DictAble):
            name: str = StrField(required=True)

        self.assertRaises(DataValidationError, lambda: Car(dict={'name': None}))
        self.assertRaises(DataValidationError, lambda: Car(dict={}))
        self.assertRaises(DataValidationError, lambda: Car(name=None))
        self.assertRaises(DataValidationError, lambda: Car())
        Car(dict={'name': 'Pramod'})

        class Car(DictAble):
            no_of_gears: int = IntField(required=True)

        try:
            Car()
        except DataValidationError as e:
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
            type: EmployeeType
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
        self.assertRaises(DataValidationError, lambda: Employee(dict=d))
        d = {
            'emp_id': 23,
            'type': 'TESTER',
            'roles': ['ADMIN', 'MANAGER', 2]
        }
        try:
            Employee(dict=d)
        except DataValidationError as e:
            self.assertEqual(e.path, 'type')
            self.assertEqual(e.err, "Pre check failed: Invalid key 'TESTER' for EmployeeType")

    def test_datetime(self):
        class User(DictAble):
            date: datetime = DatetimeField(required=True)

        self.assertRaises(DataValidationError, lambda: User(date=None))

    def test_wrong_type(self):
        class User(DictAble):
            num: int = IntField(required=True)

        self.assertRaises(DataValidationError, lambda: User(dict={'num': '1'}))
        self.assertRaises(DataValidationError, lambda: User(dict={'num': None}))
        u = User(dict={'num': 1})
        self.assertEqual(1, u.num)
        self.assertRaises(DataValidationError, lambda: User())
        self.assertRaises(DataValidationError, lambda: User(num='1'))
        self.assertEqual(1, User(num=1).num)

    def test_input_spec(self):
        class User(DictAble):
            num: int = IntField(required=True)

        self.assertEqual(User.get_input_spec(), {
            'num': {
                'type': 'IntField',
                'required': True,
            }
        })

    def test_dict_field(self):
        class User(DictAble):
            meta: dict = DictField(required=True)

        u = User(meta={'name': 'Pramod'})
        self.assertEqual('Pramod', u.meta['name'])
        self.assertRaises(DataValidationError, lambda: User())
        u = User(dict={'meta': {'name': 'Pramod'}})
        self.assertEqual('Pramod', u.meta['name'])
        self.assertRaises(DataValidationError, lambda: User(dict={'meta': 1}))
        self.assertEqual({'meta': {'name': 'Pramod'}}, u.to_dict())

    def test_pre_post_validate(self):
        class User(DictAble):
            meta: dict = DictField(required=True)

        self.assertRaises(DataValidationError, lambda: User())
        self.assertRaises(DataValidationError, lambda: User(meta=3))
        User(meta={})
        self.assertRaises(DataValidationError, lambda: User(dict={}))
        self.assertRaises(DataValidationError, lambda: User(dict={'meta': 4}))
        self.assertRaises(DataValidationError, lambda: User(dict={'meta': False}))
        User(dict={'meta': {}})

    def test_dict_value_field(self):
        class Address(DictAble):
            pin: str = StrField(required=True)

        class User(DictAble):
            pins: Dict[str, Address] = DictValueField(Address)

        User()
        User(dict={})

        class User(DictAble):
            pins: Dict[str, Address] = DictValueField(Address)

        User(pins={'a': Address(pin='333')})
        User(dict={'pins': {'a': {'pin': '333'}}})

    def test_union_field(self):
        class User(DictAble):
            roll_no = UnionField([IntField(), StrField()])

        self.assertEqual(User(roll_no="1").roll_no, "1")
        self.assertEqual(User(roll_no=1).roll_no, 1)

    def test_type_hints(self):
        class Address(DictAble):
            pin: Optional[str]

        self.assertEqual(Address(pin=None).pin, None)
        self.assertRaises(DataValidationError, lambda: Address(pin=3))

        class Address(DictAble):
            pin: str

        self.assertEqual(Address(pin='123456').pin, '123456')
        self.assertRaises(DataValidationError, lambda: Address(pin=12))
        self.assertRaises(DataValidationError, lambda: Address(pin=None))

        class HealthCard(DictAble):
            weight: Union[int, float]

        self.assertRaises(DataValidationError, lambda: HealthCard())
        self.assertRaises(DataValidationError, lambda: HealthCard(weight='79'))
        self.assertEqual(HealthCard(weight=79).weight, 79)
        self.assertEqual(HealthCard(weight=80.7).weight, 80.7)
        self.assertEqual(HealthCard(dict={'weight': 80.7}).weight, 80.7)
        self.assertRaises(DataValidationError, lambda: HealthCard(dict={}))
        self.assertRaises(DataValidationError, lambda: HealthCard(dict={'weight': '79'}))

        class WheelConfig(DictAble):
            side: str
            fixed: bool
            engineer_names: List[str]

        class Car(DictAble):
            wheel_config: WheelConfig

        car = Car(wheel_config=WheelConfig(side='left', fixed=True, engineer_names=['Pramod']))
        self.assertEqual(car.wheel_config.side, 'left')
        self.assertTrue('Pramod' in car.wheel_config.engineer_names)
        self.assertTrue(car.wheel_config.fixed)
        car = Car(dict={
            'wheel_config': {
                'side': 'right',
                'fixed': False,
                'engineer_names': []
            }
        })
        self.assertEqual(car.wheel_config.side, 'right')
        self.assertFalse('Pramod' in car.wheel_config.engineer_names)
        self.assertFalse(car.wheel_config.fixed)

        class Car(DictAble):
            wheel_config: List[WheelConfig]

        try:
            Car(dict={
                'wheel_config': {
                    'side': 'right',
                    'fixed': False,
                    'engineer_names': []
                }
            })
            raise AssertionError('It should fail')
        except DataValidationError:
            pass

        car = Car(dict={
            'wheel_config': [
                {
                    'side': 'right',
                    'fixed': False,
                    'engineer_names': ['Kumar']
                },
                {
                    'side': 'left',
                    'fixed': True,
                    'engineer_names': ['Pramod']
                }
            ]
        })
        self.assertEqual(len(car.wheel_config), 2)
        self.assertEqual(car.wheel_config[0].side, 'right')
        self.assertEqual(car.wheel_config[1].side, 'left')

    def test_error(self):
        class Size(DictAble):
            h: float
            w: float
            gaps: List[int]
            id: Union[int, str]

        class Avatar(DictAble):
            url: str
            size: Size

        class User(DictAble):
            name: str
            avatar: Avatar

        try:
            User(dict={
                'name': 'Pramod',
                'avatar': {'url': 'some', 'size': {'h': 2.3, 'w': 1.4, 'gaps': [3, 4], 'id': 2.2}}
            })
            raise AssertionError('It should fail')
        except DataValidationError as e:
            self.assertEqual(e.path, 'avatar.size.id')

        try:
            User(dict={})
            raise AssertionError('It should fail')
        except DataValidationError as e:
            self.assertEqual(e.path, 'name')

        try:
            User(dict={'name': 'Pramod', 'avatar': {}})
            raise AssertionError('It should fail')
        except DataValidationError as e:
            self.assertEqual(e.path, 'avatar.url')

        try:
            User(dict={'name': 'Pramod', 'avatar': {'url': 'https://some.com'}})
            raise AssertionError('It should fail')
        except DataValidationError as e:
            self.assertEqual(e.path, 'avatar.size')

        try:
            User(dict={'name': 'Pramod', 'avatar': {'url': 'https://some.com', 'size': {}}})
            raise AssertionError('It should fail')
        except DataValidationError as e:
            self.assertEqual(e.path, 'avatar.size.h')

        try:
            User(dict={'name': 'Pramod', 'avatar': {'url': 'https://some.com', 'size': {'h': 3., 'w': 4.}}})
            raise AssertionError('It should fail')
        except DataValidationError as e:
            self.assertEqual(e.path, 'avatar.size.gaps')

        try:
            User(dict={
                'name': 'Pramod',
                'avatar': {
                    'url': 'https://some.com',
                    'size': {
                        'h': 3.,
                        'w': 4.,
                        'id': 3,
                        'gaps': [1, 2, '3', 4]
                    },
                }
            })
            raise AssertionError('It should fail')
        except DataValidationError as e:
            self.assertEqual(e.path, 'avatar.size.gaps.[2]')

        user = User(
            name='Pramod',
            avatar=Avatar(
                url='https://some.com',
                size=Size(
                    h=2.,
                    w=1.2,
                    id=10,
                    gaps=[1, 2, 3, 4]
                )
            )
        )

        self.assertEqual(
            user.to_dict(),
            {'name': 'Pramod',
             'avatar': {'url': 'https://some.com', 'size': {'h': 2.0, 'w': 1.2, 'gaps': [1, 2, 3, 4], 'id': 10}}}
        )

        self.assertEqual(
            User.get_input_spec(),
            {
                'name': {
                    'type': 'StrField',
                    'required': True,
                },
                'avatar': {
                    'type': 'ObjectField',
                    'required': True,
                    'of': {
                        'url': {
                            'type': 'StrField',
                            'required': True,
                        },
                        'size': {
                            'type': 'ObjectField',
                            'required': True,
                            'of': {
                                'h': {
                                    'type': 'FloatField',
                                    'required': True,
                                },
                                'w': {
                                    'type': 'FloatField',
                                    'required': True,
                                },
                                'gaps': {
                                    'type': 'ListField',
                                    'required': True,
                                    'of': {
                                        'type': 'IntField',
                                        'required': True,
                                    }
                                },
                                'id': {
                                    'type': 'UnionField',
                                    'required': True,
                                    'of': [
                                        {
                                            'type': 'IntField',
                                            'required': True,
                                        },
                                        {
                                            'type': 'StrField',
                                            'required': True,
                                        }
                                    ]
                                }
                            }
                        }
                    }
                }
            }
        )

    def test_enum_with_type_hints(self):
        class CustomerType(Enum):
            regular = 'reg'
            premium = 'pre'
            vip = 3

        class Customer(DictAble):
            type: CustomerType

        self.assertEqual(Customer(dict={'type': 'regular'}).type, CustomerType.regular)
        self.assertEqual(Customer(dict={'type': 'vip'}).type, CustomerType.vip)
        self.assertEqual(Customer(type=CustomerType.premium).type, CustomerType.premium)
        self.assertRaises(DataValidationError, lambda: Customer())

        self.assertEqual(
            Customer.get_input_spec(),
            {'type': {'type': 'EnumField', 'required': True, 'of': ['regular', 'premium', 'vip']}}
        )

    def test_datetime_with_type_hints(self):
        class User(DictAble):
            dob: datetime

        self.assertEqual(User(dob=datetime(2022, 12, 31)).dob, datetime(2022, 12, 31))
        self.assertEqual(User(dob=datetime(2022, 12, 31)).to_dict()['dob'], 1672425000000)
        self.assertEqual(User(dict={'dob': 1672425000000}).dob, datetime(2022, 12, 31))
        self.assertEqual(User.get_input_spec(), {'dob': {'type': 'DatetimeField', 'required': True}})

    def test_default_value(self):
        class Address(DictAble):
            pin_code: int = IntField(default=560090)
            street: str = StrField()

        input_dict = {'street': 'RT Nagar'}
        address = Address(dict=input_dict)
        self.assertEqual(address.pin_code, 560090)
        self.assertEqual(address.street, 'RT Nagar')

        input_dict = {'pin_code': 560081, 'street': 'RT Nagar'}
        address = Address(dict=input_dict)
        self.assertEqual(address.pin_code, 560081)
        self.assertEqual(address.street, 'RT Nagar')

        class DateMillisField(IntField):
            def validate_dict(self, field_name: str, v):
                super().validate_dict(field_name, v)
                assert len(str(v)) == 13, "Length should be 13"

        class User(DictAble):
            name: str = StrField(required=True)
            time_stamp: int = DateMillisField(default=1673442076263)

        input_dict = {'name': 'Pramod'}
        user = User(dict=input_dict)
        self.assertEqual(user.name, 'Pramod')
        self.assertEqual(user.time_stamp, 1673442076263)

        class Email(DictAble):
            to: str = StrField(required=True)
            subject: str = StrField(default="General inquiry")
            body: str = StrField(required=True)

        input_dict = {'to': 'testing@gmail.com', 'body': "Hello"}
        email = Email(dict=input_dict)
        self.assertEqual(email.to, 'testing@gmail.com')
        self.assertEqual(email.subject, 'General inquiry')
        self.assertEqual(email.body, 'Hello')

        input_dict = {'to': 'testing@gmail.com', 'subject': 'Issue', 'body': "Hello"}
        email = Email(dict=input_dict)
        self.assertEqual(email.to, 'testing@gmail.com')
        self.assertEqual(email.subject, 'Issue')
        self.assertEqual(email.body, 'Hello')

        class UserInfo(DictAble):
            name: str = StrField(required=True, default=123)
            dob: int = DateMillisField(default="1673442076263")

        try:
            UserInfo(dict={'name': 'Pramod'})
        except DataValidationError as e:
            self.assertEqual(e.err, 'Pre check failed: Invalid value 1673442076263 for field dob')

        try:
            UserInfo(dict={'dob': 1673442076263})
        except DataValidationError as e:
            self.assertEqual(e.err, 'Pre check failed: Invalid value 123 for field name')

    def test_polymorphism(self):
        class Homo(DictAble):
            name: str

        class Neanderthal(Homo):
            animals_killed: int

        class Sapien(Homo):
            words_spoken: int

        class Human(DictAble):
            species: Homo = MultiTypeField([Neanderthal, Sapien])

        human = Human(dict={
            'species': {
                'name': 'Mufasa',
                'words_spoken': 1024,
                '__type': 'Sapien'
            }
        })
        self.assertEqual(human.species.name, 'Mufasa')
        self.assertTrue(isinstance(human.species, Sapien))
        assert isinstance(human.species, Sapien)
        self.assertEqual(human.species.words_spoken, 1024)

    def test_type_dict(self):
        class Village(DictAble):
            people: Dict

        self.assertEqual(Village(dict={'people': {'pramod': 30}}).people['pramod'], 30)
        self.assertEqual(Village(dict={'people': {1: 30}}).people[1], 30)
        self.assertEqual(Village(dict={'people': {1: (1, 2)}}).people[1], (1, 2))
        self.assertRaises(DataValidationError, lambda: Village(dict={'people': 3}))

        class Village(DictAble):
            people: Dict[str, str]

        self.assertRaises(DataValidationError, lambda: Village(dict={'people': 3}))
        self.assertRaises(DataValidationError, lambda: Village(dict={'people': {1: 30}}))
        self.assertEqual(Village(dict={'people': {'pramod': 'Pramod'}}).people['pramod'], 'Pramod')

        class Human(DictAble):
            age: int

        class Village(DictAble):
            people: Dict[str, Human]

        village = Village(dict={'people': {'pramod': {'age': 30}}})
        self.assertEqual(village.people['pramod'].age, 30)

        try:
            Village(dict={'people': {'pramod': {'age': 'hi'}}})
            raise AssertionError('Should not have passed!')
        except DataValidationError as e:
            self.assertEqual(e.path, 'people.pramod.age')

        try:
            Village(dict={
                'people': {
                    'satyam': {'age': 'hi'},
                    'pramod': {'age': 30}
                }
            })
            raise AssertionError('Should not have passed!')
        except DataValidationError as e:
            self.assertEqual(e.path, 'people.satyam.age')

    def test_nested_optional_list(self):
        class RefSchema(DictAble):
            referenceName: str = StrField(required=False)

        class Address(DictAble):
            location: str
            references: List[RefSchema] = ListField(ObjectField(RefSchema, required=False), required=False)

        class Profile(DictAble):
            address: Address = ObjectField(Address)

        profile = Profile(dict={'address': {'location': 'Bengaluru'}})
        self.assertEqual(profile.address.references, None)
        self.assertEqual(profile.to_dict(), {'address': {'references': None, 'location': 'Bengaluru'}})

    def test_dynamic_default(self):
        now = datetime.now()

        class DOB(DictAble):
            date: datetime = DatetimeField(default=now)

        self.assertEqual(DOB().date, now)
        _now = datetime(2023, 5, 19)
        self.assertEqual(DOB(date=_now).date, _now)

        self.assertEqual(DOB(dict={}).date, now)
        self.assertEqual(DOB(dict={'date': None}).date, now)

        millis = 1684462306000
        self.assertEqual(DOB(dict={'date': millis}).date, datetime.fromtimestamp(millis / 1000))

        class DOB(DictAble):
            date: datetime = DatetimeField(default_factory=(datetime.now, (), {}))
            date_2: datetime = DatetimeField(default=datetime.now())

        self.assertLessEqual((DOB().date - datetime.now()).total_seconds(), 1e2)

        dob1 = DOB()
        sleep(1)
        dob2 = DOB()

        self.assertEqual(dob1.date_2, dob2.date_2)
        self.assertLessEqual((dob2.date - dob1.date).total_seconds(), 1 + 1e2)

        def math(a: int, b: int):
            return a * b

        class Number(DictAble):
            num: int = IntField(default_factory=(math, (8,), {'b': 5}))

        self.assertEqual(Number().num, 40)
        self.assertEqual(Number(dict={'num': None}).num, 40)
        self.assertEqual(Number(dict={'num': 5}).num, 5)

    def test_regex(self):
        class Profile(DictAble):
            panNumber: str = RegexField(required=False, regex_string=r"^[A-Z]{5}[0-9]{4}[A-Z]$")
            email: str = RegexField(regex_string=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")

        try:
            Profile(dict={'email': 'xyz'})
        except DataValidationError as e:
            self.assertEqual(e.err, 'Pre check failed: xyz for email should be in proper format')

        try:
            Profile(dict={'email': 1234567})
        except DataValidationError as e:
            self.assertEqual(e.err, 'Pre check failed: Invalid value 1234567 for field email')

        try:
            Profile(dict={'email': 'abc@gmail.com', 'panNumber': '12345'})
        except DataValidationError as e:
            self.assertEqual(e.err, 'Pre check failed: 12345 for panNumber should be in proper format')

        profile = Profile(dict={'email': 'abc@gmail.com', 'panNumber': 'ABCDE1234H'})

        self.assertEqual(
            profile.get_input_spec(),
            {
                'email': {
                    'type': 'RegexField', 'required': False,
                    'of': {'regex': '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$'}
                },
                'panNumber': {'type': 'RegexField', 'required': False, 'of': {'regex': '^[A-Z]{5}[0-9]{4}[A-Z]$'}}
            }
        )

    def test_range(self):
        class Profile(DictAble):
            salary: int = RangeIntField(required=False, max_val=100000, min_val=1000)
            expenses: float = RangeFloatField(required=False, max_val=10000.0)
            donation: float = RangeFloatField(required=False, min_val=100.0)

        try:
            Profile(dict={'salary': 10000000})
        except DataValidationError as e:
            self.assertEqual(e.err, 'Pre check failed: 10000000 for salary should be in range 1000 to 100000')

        try:
            Profile(dict={'salary': True})
        except DataValidationError as e:
            self.assertEqual(e.err, 'Pre check failed: True for salary should be in range 1000 to 100000')

        try:
            Profile(dict={'salary': 10000, 'expenses': 100000.0})
        except DataValidationError as e:
            self.assertEqual(e.err, 'Pre check failed: 100000.0 for expenses should be in range 0.0 to 10000.0')

        try:
            Profile(dict={'salary': 10000, 'expenses': '100000.0'})
        except DataValidationError as e:
            self.assertEqual(e.err, 'Pre check failed: Invalid value 100000.0 for field expenses')

        try:
            Profile(dict={'salary': 100000, 'expenses': 1000.0, 'donation': 10.0})
        except DataValidationError as e:
            self.assertEqual(e.err, 'Pre check failed: 10.0 for donation should be in range 100.0 to inf')

        profile = Profile(dict={'salary': 10000, 'expenses': 1000.0, 'donation': 1000.0})

        self.assertEqual(
            profile.get_input_spec(),
            {
                'donation': {'type': 'RangeFloatField', 'required': False, 'of': {'min': 100, 'max': math.inf}},
                'expenses': {'type': 'RangeFloatField', 'required': False, 'of': {'min': 0.0, 'max': 10000}},
                'salary': {'type': 'RangeIntField', 'required': False, 'of': {'min': 1000, 'max': 100000}}
            }
        )

    def test_partial(self):
        class Account(Enum):
            INTEREST_DUE = 'INTEREST_DUE'
            PRINCIPAL_DUE = 'PRINCIPAL_DUE'
            CHARGE_DUE = 'CHARGE_DUE'

        class CFMode(Enum):
            DUE = 'DUE'
            DEDUCT = 'DEDUCT'

        class EPIConfig(DictAble):
            cycle_duration: int
            n_cycles: int
            first_due_delta_days: int
            first_due_weekday: Optional[int] = IntField(required=False)
            first_due_day_of_month: Optional[int] = IntField(required=False)

        class ProductConfig(DictAble):
            allocation_policy: List[List[Account]] = ListField(
                ListField(EnumField(Account, required=True), required=True), required=True
            )
            epi_config: Optional[EPIConfig] = ObjectField(EPIConfig, required=True)
            lpp_pct: float
            cf_mode: CFMode
            po_due_pct: int
            is_co_lent: bool

        partial_product_config = partial(ProductConfig)
        fields = partial_product_config.get_fields()
        self.assertEqual(partial_product_config.__name__, 'PartialProductConfig')
        self.assertEqual(fields['allocation_policy'].required, False)
        self.assertEqual(fields['allocation_policy'].spec()['of']['required'], True)
        self.assertEqual(fields['allocation_policy'].spec()['of']['of']['required'], True)
        self.assertEqual(fields['epi_config'].required, False)
        self.assertEqual(fields['epi_config'].spec()['of']['cycle_duration']['required'], True)
        self.assertEqual(fields['epi_config'].spec()['of']['n_cycles']['required'], True)
        self.assertEqual(fields['epi_config'].spec()['of']['first_due_delta_days']['required'], True)
        self.assertEqual(fields['lpp_pct'].required, False)
        self.assertEqual(fields['cf_mode'].required, False)
        self.assertEqual(fields['po_due_pct'].required, False)
        self.assertEqual(fields['is_co_lent'].required, False)

    def test_skip_optional(self):
        class Address(DictAble):
            city: str = StrField()
            pin_code: int = IntField()

        class Person(DictAble):
            name: str = StrField()
            address: Address = ObjectField(Address)

        p = Person()
        self.assertEqual(p.to_dict(), {'address': None, 'name': None})
        self.assertEqual(p.to_dict(skip_optional=True), {})

        p = Person(dict={'address': {}, 'name': 'Pramod'})
        self.assertEqual(p.to_dict(), {'address': {'city': None, 'pin_code': None}, 'name': 'Pramod'})
        self.assertEqual(p.to_dict(skip_optional=True), {'address': {}, 'name': 'Pramod'})

        p = Person(dict={'address': {'pin_code': 560001}, 'name': 'Pramod'})
        self.assertEqual(p.to_dict(), {'address': {'city': None, 'pin_code': 560001}, 'name': 'Pramod'})
        self.assertEqual(p.to_dict(skip_optional=True), {'address': {'pin_code': 560001}, 'name': 'Pramod'})

        class Car(DictAble):
            model: str = StrField(required=True)
            name: str = StrField()

        class Person2(DictAble):
            name: str = StrField()
            address: Address = ObjectField(Address)
            cars: List[Car] = ListField(UnionField([ObjectField(Car), NoneField()]), required=True)

        p = Person2(dict={'cars': [None]})
        self.assertEqual(p.to_dict(), {'address': None, 'cars': [None], 'name': None})
        self.assertEqual(p.to_dict(skip_optional=True), {'cars': [None]})

        p = Person2(dict={'cars': [None, {'model': 'i20'}]})
        self.assertEqual(p.to_dict(), {
            'address': None,
            'cars': [None, {'model': 'i20', 'name': None}],
            'name': None
        })
        self.assertEqual(p.to_dict(skip_optional=True), {'cars': [None, {'model': 'i20'}]})
