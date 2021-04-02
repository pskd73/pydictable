import inspect
from abc import abstractmethod, ABC
from datetime import datetime
from typing import Dict, Type, List


class Field:
    def __init__(self, optional: bool=True):
        self.optional = optional

    def validate(self, v):
        try:
            self.validate_value(v)
        except AssertionError:
            if not (self.optional and v is None):
                raise ValueError('Invalid value {} for field {}'.format(v, self.__class__.__name__))

    @abstractmethod
    def from_json(self, v):
        pass

    @abstractmethod
    def to_json(self, v):
        pass

    @abstractmethod
    def validate_value(self, v):
        pass


class DictAble:
    def __init__(self, *args, **kwargs):
        self.__apply_dict(self, {})
        for k, v in kwargs.items():
            if k in self.__get_fields(self):
                self.__setattr__(k, v)
        if kwargs.get('dict'):
            self.__apply_dict(self, kwargs['dict'])
        if len(args) > 0:
            raise ReferenceError('Use kwargs to init DictAble')
        self.__validate()

    @staticmethod
    def __get_fields(obj) -> Dict[str, Field]:
        fields = {}
        for attr in inspect.getmembers(obj.__class__):
            if isinstance(attr[1], Field):
                fields[attr[0]] = attr[1]
        return fields

    @staticmethod
    def __apply_dict(obj, d: dict):
        for attr, field in DictAble.__get_fields(obj).items():
            obj.__setattr__(attr, field.from_json(d.get(attr)))

    def __validate(self):
        for attr, field in DictAble.__get_fields(self).items():
            field.validate(self.__getattribute__(attr))

    def to_json(self) -> dict:
        return {attr: field.to_json(self.__getattribute__(attr)) for attr, field in self.__get_fields(self).items()}


class StrField(Field):
    def from_json(self, v: str):
        return v

    def to_json(self, v):
        return v

    def validate_value(self, v):
        assert type(v) == str


class IntField(Field):
    def from_json(self, v: int):
        return v

    def to_json(self, v):
        return v

    def validate_value(self, v):
        assert type(v) == int


class FloatField(Field):
    def from_json(self, v):
        return v

    def to_json(self, v):
        return v

    def validate_value(self, v):
        assert type(v) == float


class DatetimeField(Field):
    def from_json(self, v: int):
        if v is None:
            return None
        return datetime.fromtimestamp(v / 1000)

    def to_json(self, v: datetime):
        return int(v.timestamp() * 1000)

    def validate_value(self, v):
        return type(v) == datetime


class ObjectField(Field):
    def __init__(self, obj_type: Type[DictAble], optional: bool=True):
        super(ObjectField, self).__init__(optional=optional)
        self.obj_type = obj_type

    def from_json(self, v):
        if v is None:
            return None
        return self.obj_type(dict=v)

    def to_json(self, v):
        return v.to_json()

    def validate_value(self, v):
        assert isinstance(v, DictAble)


class ListField(Field):
    def __init__(self, obj_type: Field, optional: bool=True):
        super(ListField, self).__init__(optional=optional)
        self.obj_type = obj_type

    def from_json(self, v):
        if v is None:
            return None
        return [self.obj_type.from_json(e) for e in v]

    def to_json(self, v):
        return [self.obj_type.to_json(e) for e in v]

    def validate_value(self, v):
        assert type(v) == list and False not in set([self.obj_type.validate(e) for e in v])


class CustomField(Field, ABC):
    """
    For advance usage
    """
    def __init__(self, from_json, to_json, optional: bool=True):
        super(CustomField, self).__init__(optional=optional)
        self._from_json = from_json
        self._to_json = to_json

    def from_json(self, v):
        return self._from_json(v)

    def to_json(self, v):
        return self._to_json(v)


class MultiTypeField(CustomField):
    TYPE_KEY = '__type'

    def __init__(self, types: List[Type[DictAble]], optional: bool=True):
        self.types_dict = {t.__name__: t for t in types}
        super(MultiTypeField, self).__init__(
            lambda d: self.types_dict[d[self.TYPE_KEY]](dict=d),
            lambda o: {**o.to_json(), self.TYPE_KEY: o.__class__.__name__},
            optional=optional
        )

    def validate_value(self, v):
        assert v.__class__.__name__ in self.types_dict


class Person(DictAble):
    name: str = StrField()
    age: int = IntField(optional=True)


p = Person(name='Pramod', age=3)
