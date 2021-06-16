# pydictable
Make your classes json serializable and deserializable. It supports **from dict** and **to dict** with proper **attribute hints**. Best usecase would be

1. Let us say you store json in s3. When you fetch it, you want it to be an object instead of a dict.
2. When you want to store the object back to s3, you want to convert it to dict.

NamedTuple would come handy in this situation, but as it is tuple, it is immutable. You can do these two operations easily with DictAble.

### 💾 Installation
```
pip install pydictable
```

### 💡 Example
```python 

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
p.name # Pramod
p.address # Address object
p.address.pin_code # 560032

p.to_dict() == input_dict # Not order though!

p.address.pin_code = 518466 # You can change the values

# you can initiate with named params too
p2 = Person(
    name='Pramod',
    address=Address(
        pin_code=560032,
        lat_lng=LatLng(
            lat=12345,
            lng=67890
        )
    )
)
p == p2 # shallow equal
p2.to_dict() == p.to_dict()

```

### 📜 Fields
##### StrField
##### IntField
##### FloatField
##### DictField
##### DatetimeField
##### ObjectField
```
__init__(self, obj_type: Type[DictAble])
```
##### ListField
```
__init__(self, obj_type: Field)
```
##### MultiTypeField
```
__init__(self, types: List[Type[DictAble]])
```
```python
class Car(DictAble):
    name: str = StrField()

class CarA(Car):
    a_field: str = StrField()

class CarB(Car):
    b_field: str = StrField()

class Garage(DictAble):
    cars: List[Car] = ListField(MultiTypeField([CarA, CarB]))

g = Garage(
    cars=[
        CarA(name='i20', a_field='some value')
    ]
)
g.to_dict() # {'cars': [{'a_field': 'some value', 'name': 'i20', '__type': 'CarA'}]}
```

It is still under development. Feel free to report bugs or push changes! Cheers!
