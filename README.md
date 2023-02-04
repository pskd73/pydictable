# pydictable
![Coverage](./reports/coverage/badge.svg)

A pure python, zero dependency solution for 
1. Schema (json/dict) validation
2. Serialize/Deserialize to json

### Installation
```
pip install pydictable
```

### Example
```python 

class LatLng(DictAble):
    lat: int
    lng: int

class Address(DictAble):
    pin_code: int
    lat_lng: LatLng

class Person(DictAble):
    name: str
    address: Address

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

p = Person(dict=input_dict) # Raises DataValidationError if not valid
p.name # Pramod
p.address # Address object
p.address.pin_code # 560032

p.to_dict() == input_dict # Serialize

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

Person.get_input_schema() # Get the Schema spec as json!
```

### Extendability
You can quickly build your own fields as explained below
```python
class PositiveIntField(IntField):
    def validate_json(self, field_name: str, v):
        assert v > 0, 'Should be positive integer'

class Person(DictAble):
    age: int = PositiveIntField()

Person(dict={'age': -1}) # Raises DataValidationError
```

Feel free to report bugs or push changes! Cheers!
