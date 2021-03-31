import inspect
from abc import abstractmethod
from typing import Dict, Type


class Field:
    @abstractmethod
    def get_type(self):
        pass

    @abstractmethod
    def from_json(self, v):
        pass

    @abstractmethod
    def to_json(self, v):
        pass


class DictAble:
    def __init__(self, *args, **kwargs):
        self.__apply_dict(self, {})
        self.__apply_dict(self, kwargs)
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

    def get_type(self):
        return str


class IntField(Field):
    def from_json(self, v: int):
        return v

    def to_json(self, v):
        return v

    def get_type(self):
        return int


class FloatField(Field):
    def get_type(self):
        return float

    def from_json(self, v):
        return v

    def to_json(self, v):
        return v


class ObjectField(Field):
    def __init__(self, obj_type: Type[DictAble]):
        self.obj_type = obj_type

    def from_json(self, v):
        if v is None:
            return None
        return self.obj_type(**v)

    def to_json(self, v):
        return v.to_json()

    def get_type(self):
        return self.obj_type


class ListField(Field):
    def __init__(self, obj_type: Field):
        self.obj_type = obj_type

    def from_json(self, v):
        if v is None:
            return None
        return [self.obj_type.from_json(e) for e in v]

    def to_json(self, v):
        return [self.obj_type.to_json(e) for e in v]

    def get_type(self):
        return list
