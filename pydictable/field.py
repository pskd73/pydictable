from abc import ABC
from datetime import datetime
from typing import Type, List

from pydictable.core import Field, DictAble


class StrField(Field):
    def from_json(self, v: str):
        return v

    def to_json(self, v):
        return v

    def validate_value(self, field_name: str, v):
        assert type(v) == str


class IntField(Field):
    def from_json(self, v: int):
        return v

    def to_json(self, v):
        return v

    def validate_value(self, field_name: str, v):
        assert type(v) == int


class FloatField(Field):
    def from_json(self, v):
        return v

    def to_json(self, v):
        return v

    def validate_value(self, field_name: str, v):
        assert type(v) == float


class DatetimeField(Field):
    def from_json(self, v: int):
        if v is None:
            return None
        return datetime.fromtimestamp(v / 1000)

    def to_json(self, v: datetime):
        return int(v.timestamp() * 1000)

    def validate_value(self, field_name: str, v):
        return type(v) == datetime


class ObjectField(Field):
    def __init__(self, obj_type: Type[DictAble], required: bool=False):
        super(ObjectField, self).__init__(required=required)
        self.obj_type = obj_type

    def from_json(self, v):
        if v is None:
            return None
        return self.obj_type(dict=v)

    def to_json(self, v):
        return v.to_json()

    def validate_value(self, field_name: str, v):
        assert isinstance(v, DictAble)


class ListField(Field):
    def __init__(self, obj_type: Field, required: bool=False):
        super(ListField, self).__init__(required=required)
        self.obj_type = obj_type

    def from_json(self, v):
        if v is None:
            return None
        return [self.obj_type.from_json(e) for e in v]

    def to_json(self, v):
        return [self.obj_type.to_json(e) for e in v]

    def validate_value(self, field_name: str, v):
        assert type(v) == list and False not in set([self.obj_type.validate(field_name, e) for e in v])


class CustomField(Field, ABC):
    """
    For advance usage
    """
    def __init__(self, from_json, to_json, required: bool=False):
        super(CustomField, self).__init__(required=required)
        self._from_json = from_json
        self._to_json = to_json

    def from_json(self, v):
        return self._from_json(v)

    def to_json(self, v):
        return self._to_json(v)


class MultiTypeField(CustomField):
    TYPE_KEY = '__type'

    def __init__(self, types: List[Type[DictAble]], required: bool=False):
        self.types_dict = {t.__name__: t for t in types}
        super(MultiTypeField, self).__init__(
            lambda d: self.types_dict[d[self.TYPE_KEY]](dict=d),
            lambda o: {**o.to_json(), self.TYPE_KEY: o.__class__.__name__},
            required=required
        )

    def validate_value(self, field_name: str, v):
        assert v.__class__.__name__ in self.types_dict