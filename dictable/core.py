import inspect
from abc import abstractmethod
from datetime import datetime
from typing import Dict, Type, List


class Field:
    @abstractmethod
    def from_json(self, v):
        pass

    @abstractmethod
    def to_json(self, v):
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

    def to_json(self) -> dict:
        return {attr: field.to_json(self.__getattribute__(attr)) for attr, field in self.__get_fields(self).items()}


class StrField(Field):
    def from_json(self, v: str):
        return v

    def to_json(self, v):
        return v


class IntField(Field):
    def from_json(self, v: int):
        return v

    def to_json(self, v):
        return v


class FloatField(Field):
    def from_json(self, v):
        return v

    def to_json(self, v):
        return v


class DatetimeField(Field):
    def from_json(self, v: int):
        if v is None:
            return None
        return datetime.fromtimestamp(v / 1000)

    def to_json(self, v: datetime):
        return int(v.timestamp() * 1000)


class ObjectField(Field):
    def __init__(self, obj_type: Type[DictAble]):
        self.obj_type = obj_type

    def from_json(self, v):
        if v is None:
            return None
        return self.obj_type(dict=v)

    def to_json(self, v):
        return v.to_json()


class ListField(Field):
    def __init__(self, obj_type: Field):
        self.obj_type = obj_type

    def from_json(self, v):
        if v is None:
            return None
        return [self.obj_type.from_json(e) for e in v]

    def to_json(self, v):
        return [self.obj_type.to_json(e) for e in v]


class CustomField(Field):
    """
    For advance usage
    """
    def __init__(self, from_json, to_json):
        self._from_json = from_json
        self._to_json = to_json

    def from_json(self, v):
        return self._from_json(v)

    def to_json(self, v):
        return self._to_json(v)


class MultiTypeField(CustomField):
    TYPE_KEY = '__type'

    def __init__(self, types: List[Type[DictAble]]):
        types_dict = {t.__name__: t for t in types}
        super(MultiTypeField, self).__init__(
            lambda d: types_dict[d[self.TYPE_KEY]](dict=d),
            lambda o: {**o.to_json(), self.TYPE_KEY: o.__class__.__name__}
        )
