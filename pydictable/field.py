from abc import ABC
from datetime import datetime
from enum import EnumMeta, Enum
from typing import Type, List

from pydictable.core import Field, DictAble


class StrField(Field):
    def from_dict(self, v: str):
        return v

    def to_dict(self, v):
        return v

    def validate_dict(self, field_name: str, v):
        assert type(v) == str

    def validate(self, field_name: str, v):
        assert type(v) == str


class BoolField(Field):
    def from_dict(self, v: bool):
        return v

    def to_dict(self, v):
        return v

    def validate_dict(self, field_name: str, v):
        assert type(v) == bool

    def validate(self, field_name: str, v):
        assert type(v) == bool


class IntField(Field):
    def from_dict(self, v: int):
        return v

    def to_dict(self, v):
        return v

    def validate_dict(self, field_name: str, v):
        assert type(v) == int

    def validate(self, field_name: str, v):
        assert type(v) == int


class FloatField(Field):
    def from_dict(self, v):
        return v

    def to_dict(self, v):
        return v

    def validate_dict(self, field_name: str, v):
        assert type(v) == float

    def validate(self, field_name: str, v):
        assert type(v) == float


class DatetimeField(Field):
    def from_dict(self, v: int):
        return datetime.fromtimestamp(v / 1000)

    def to_dict(self, v: datetime):
        return int(v.timestamp() * 1000)

    def validate_dict(self, field_name: str, v):
        assert type(v) == int

    def validate(self, field_name: str, v):
        assert isinstance(v, datetime)


class ObjectField(Field):
    def __init__(self, obj_type: Type[DictAble], required: bool=False):
        super(ObjectField, self).__init__(required=required)
        self.obj_type = obj_type

    def from_dict(self, v):
        return self.obj_type(dict=v)

    def to_dict(self, v):
        return None if v is None else v.to_dict()

    def validate_dict(self, field_name: str, v):
        self.obj_type(dict=v)

    def validate(self, field_name: str, v):
        assert isinstance(v, DictAble)


class ListField(Field):
    def __init__(self, obj_type: Field, *args, **kwargs):
        super(ListField, self).__init__(*args, **kwargs)
        self.obj_type = obj_type

    def from_dict(self, v):
        return [self.obj_type.from_dict(e) for e in v]

    def to_dict(self, v):
        return [self.obj_type.to_dict(e) for e in v]

    def validate_dict(self, field_name: str, v):
        assert type(v) == list
        [self.obj_type.validate_dict(field_name, x) for x in v]

    def validate(self, field_name: str, v):
        assert type(v) == list
        [self.obj_type.validate(field_name, x) for x in v]


class CustomField(Field, ABC):
    """
    For advance usage
    """
    def __init__(self, from_json, to_json, *args, **kwargs):
        super(CustomField, self).__init__(*args, **kwargs)
        self._from_json = from_json
        self._to_json = to_json

    def from_dict(self, v):
        return self._from_json(v)

    def to_dict(self, v):
        return self._to_json(v)


class MultiTypeField(CustomField):
    TYPE_KEY = '__type'

    def __init__(self, types: List[Type[DictAble]], *args, **kwargs):
        self.types_dict = {t.__name__: t for t in types}
        super(MultiTypeField, self).__init__(
            lambda d: self.types_dict[d[self.TYPE_KEY]](dict=d),
            lambda o: {**o.to_dict(), self.TYPE_KEY: o.__class__.__name__},
            *args, **kwargs
        )

    def validate_dict(self, field_name: str, v):
        self.types_dict[v[self.TYPE_KEY]](dict=v)

    def validate(self, field_name: str, v):
        pass


class EnumField(Field):
    def __init__(self, enum: EnumMeta, *args, **kwargs):
        super(EnumField, self).__init__(*args, **kwargs)
        self.enum = enum

    def from_dict(self, v):
        return self.enum(v)

    def to_dict(self, v):
        return v.value

    def validate_dict(self, field_name: str, v):
        try:
            self.enum(v)
        except ValueError as e:
            raise AssertionError('Invalid value')

    def validate(self, field_name: str, v):
        assert isinstance(v, Enum)


class DictField(Field):
    def from_dict(self, v):
        return v

    def to_dict(self, v):
        return v

    def validate_dict(self, field_name: str, v):
        assert type(v) == dict

    def validate(self, field_name: str, v):
        assert type(v) == dict


class DictValueField(Field):
    def __init__(self, value_type: Type[DictAble], required: bool = False, key: str = None):
        self.value_type = value_type
        super(DictValueField, self).__init__(required, key)

    def from_dict(self, v):
        return {key: self.value_type(dict=val) for key, val in v.items()}

    def to_dict(self, v):
        return {key: val.to_dict() for key, val in v.items()}

    def validate_dict(self, field_name: str, v: dict):
        assert type(v) == dict
        [self.value_type(dict=v) for v in v.values()]

    def validate(self, field_name: str, v):
        assert type(v) == dict
        for val in v.values():
            assert isinstance(val, DictAble)
