# dictable
Make your classes json serializable and deserializable. It supports **from dict** and **to dict** with proper **attribute hints**. Best usecase would be

1. Let us say you store json in s3. When you fetch it, you want it to be an object instead of a dict.
2. When you want to store the object back to s3, you want to convert it to dict.

NamedTuple would come handy in this situation, but as it is tuple, it is immutable. You can do these two operations easily with DictAble.

### Example:
```python
from dictable.core import DictAble, StrField, IntField, ObjectField, ListField        


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
p = Person(input_dict)
p.name # Pramod
p.address # Address object
p.address.pin_code # 560032

p.to_json() == input_dict # Not order though!

p.address.pin_code = 518466 # You can change the values
```

It is still under development. Feel free to report bugs or push changes!