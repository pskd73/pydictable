from typing import List

from dictable.core import DictAble, StringField, IntField, ObjectField, ListField


class Address(DictAble):
    pin_code: str = StringField()
    state: str = StringField()


class Person(DictAble):
    name: str = StringField()
    age: int = IntField()
    address: Address = ObjectField(Address)
    addresses: List[Address] = ListField(Address)


d = {'name': 'Pramod', 'age': 28, 'address': {'pin_code': '560032'}, 'addresses': [{'pin_code': '518466'}]}
p = Person(d)
print(p.address.pin_code)