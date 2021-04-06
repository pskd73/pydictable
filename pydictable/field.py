from abc import ABC
from datetime import datetime
from enum import EnumMeta
from typing import Type, List

from pydictable.core import Field, DictAble


class StrField(Field):
    def from_dict(self, v: str):
        return v

    def to_dict(self, v):
        return v

    def validate_value(self, field_name: str, v):
        assert type(v) == str


class IntField(Field):
    def from_dict(self, v: int):
        return v

    def to_dict(self, v):
        return v

    def validate_value(self, field_name: str, v):
        assert type(v) == int


class FloatField(Field):
    def from_dict(self, v):
        return v

    def to_dict(self, v):
        return v

    def validate_value(self, field_name: str, v):
        assert type(v) == float


class DatetimeField(Field):
    def from_dict(self, v: int):
        return datetime.fromtimestamp(v / 1000)

    def to_dict(self, v: datetime):
        return int(v.timestamp() * 1000)

    def validate_value(self, field_name: str, v):
        assert type(v) == datetime


class ObjectField(Field):
    def __init__(self, obj_type: Type[DictAble], required: bool=False):
        super(ObjectField, self).__init__(required=required)
        self.obj_type = obj_type

    def from_dict(self, v):
        return self.obj_type(dict=v)

    def to_dict(self, v):
        return v.to_dict()

    def validate_value(self, field_name: str, v):
        assert isinstance(v, DictAble)


class ListField(Field):
    def __init__(self, obj_type: Field, *args, **kwargs):
        super(ListField, self).__init__(*args, **kwargs)
        self.obj_type = obj_type

    def from_dict(self, v):
        return [self.obj_type.from_dict(e) for e in v]

    def to_dict(self, v):
        return [self.obj_type.to_dict(e) for e in v]

    def validate_value(self, field_name: str, v):
        assert type(v) == list and False not in set([self.obj_type.validate(field_name, e) for e in v])


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

    def validate_value(self, field_name: str, v):
        assert v.__class__.__name__ in self.types_dict


class EnumField(Field):
    def __init__(self, enum: EnumMeta, *args, **kwargs):
        super(EnumField, self).__init__(*args, **kwargs)
        self.enum = enum

    def from_dict(self, v):
        return self.enum(v)

    def to_dict(self, v):
        return v.value

    def validate_value(self, field_name: str, v):
        try:
            self.enum(v)
        except ValueError as e:
            raise AssertionError('Invalid value')
