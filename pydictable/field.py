from abc import ABC
from datetime import datetime
from enum import EnumMeta, Enum
from typing import Type, List

from pydictable.type import Field, _BaseDictAble


class DataValidationError(Exception):
    def __init__(self, path: str, err):
        super(DataValidationError, self).__init__(path, err)
        self.path = path
        self.err = err


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
    def __init__(self, obj_type: Type[_BaseDictAble], required: bool=False):
        super(ObjectField, self).__init__(required=required)
        self.obj_type = obj_type

    def from_dict(self, v):
        return self.obj_type(dict=v)

    def to_dict(self, v):
        return None if v is None else v.to_dict()

    def validate_dict(self, field_name: str, v):
        assert not self.required or v is not None
        self.obj_type(dict=v)

    def validate(self, field_name: str, v):
        assert isinstance(v, _BaseDictAble)

    def of(self):
        return self.obj_type.get_input_spec()


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
        for i, _val in enumerate(v):
            try:
                self.obj_type.validate_dict(field_name, _val)
            except AssertionError as e:
                raise DataValidationError(f'[{i}]', str(e))

    def validate(self, field_name: str, v):
        assert type(v) == list
        [self.obj_type.validate(field_name, x) for x in v]

    def of(self):
        return self.obj_type.spec()


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

    def __init__(self, types: List[Type[_BaseDictAble]], *args, **kwargs):
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
    def __init__(self, enum: EnumMeta, is_name: bool = False, *args, **kwargs):
        super(EnumField, self).__init__(*args, **kwargs)
        self.enum = enum
        self.is_name = is_name

    def from_dict(self, v):
        return self.enum[v] if self.is_name else self.enum(v)

    def to_dict(self, v):
        return v.value

    def validate_dict(self, field_name: str, v):
        try:
            self.enum[v] if self.is_name else self.enum(v)
        except ValueError as e:
            raise AssertionError('Invalid enum')
        except KeyError as e:
            raise AssertionError(f'Invalid key {e} for {self.enum.__name__}')

    def validate(self, field_name: str, v):
        assert isinstance(v, Enum)

    def of(self):
        return [e.name if self.is_name else e.value for e in self.enum]


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
    def __init__(self, value_type: Type[_BaseDictAble], required: bool = False, key: str = None):
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
            assert isinstance(val, _BaseDictAble)


class UnionField(Field):
    def __init__(self, fields: List[Field], *args, **kwargs):
        super(UnionField, self).__init__(*args, **kwargs)
        self.fields_dict = {f.__class__.__name__: f for f in fields}

    def from_dict(self, v):
        for name, field in self.fields_dict.items():
            try:
                field.validate_dict('', v)
                return field.from_dict(v)
            except AssertionError:
                pass
        raise NotImplementedError()

    def to_dict(self, v):
        for name, field in self.fields_dict.items():
            try:
                field.validate('', v)
                return field.to_dict(v)
            except AssertionError:
                pass
        raise NotImplementedError()

    def validate_dict(self, field_name: str, v):
        for name, field in self.fields_dict.items():
            try:
                field.validate_dict('', v)
                return
            except AssertionError:
                pass
        raise AssertionError(f'{v} does not match for any of {list(self.fields_dict.keys())}')

    def validate(self, field_name: str, v):
        for name, field in self.fields_dict.items():
            try:
                field.validate('', v)
                return
            except AssertionError:
                pass
        raise AssertionError(f'{v} does not match for any of {list(self.fields_dict.keys())}')

    def of(self):
        return [f.spec() for f in self.fields_dict.values()]


class NoneField(Field):
    def from_dict(self, v):
        return None

    def to_dict(self, v):
        return None

    def validate_dict(self, field_name: str, v):
        assert v is None

    def validate(self, field_name: str, v):
        assert v is None
