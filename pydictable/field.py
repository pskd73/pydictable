import math
import re
from abc import ABC
from datetime import datetime
from enum import EnumMeta, Enum
from typing import Type, List, Any

from pydictable.type import Field, _BaseDictAble, DefaultFactoryType


class DataValidationError(Exception):
    def __init__(self, path: str, err):
        super(DataValidationError, self).__init__(path, err)
        self.path = path
        self.err = err


class StrField(Field):
    def from_dict(self, v: str):
        return v

    def to_dict(self, v, skip_optional: bool = False):
        return v

    def validate_dict(self, field_name: str, v):
        assert type(v) == str

    def validate(self, field_name: str, v):
        assert type(v) == str


class BoolField(Field):
    def from_dict(self, v: bool):
        return v

    def to_dict(self, v, skip_optional: bool = False):
        return v

    def validate_dict(self, field_name: str, v):
        assert type(v) == bool

    def validate(self, field_name: str, v):
        assert type(v) == bool


class IntField(Field):
    def from_dict(self, v: int):
        return v

    def to_dict(self, v, skip_optional: bool = False):
        return v

    def validate_dict(self, field_name: str, v):
        assert type(v) == int

    def validate(self, field_name: str, v):
        assert type(v) == int


class FloatField(Field):
    def from_dict(self, v):
        return v

    def to_dict(self, v, skip_optional: bool = False):
        return v

    def validate_dict(self, field_name: str, v):
        assert type(v) == float

    def validate(self, field_name: str, v):
        assert type(v) == float


class DatetimeField(Field):
    def from_dict(self, v: int):
        return datetime.fromtimestamp(v / 1000)

    def to_dict(self, v: datetime, skip_optional: bool = False):
        return int(v.timestamp() * 1000)

    def validate_dict(self, field_name: str, v):
        assert type(v) == int

    def validate(self, field_name: str, v):
        assert isinstance(v, datetime)


class ObjectField(Field):
    def __init__(self, obj_type: Type[_BaseDictAble], required: bool = False):
        super(ObjectField, self).__init__(required=required)
        self.obj_type = obj_type

    def from_dict(self, v):
        return self.obj_type(dict=v)

    def to_dict(self, v, skip_optional: bool = False):
        return None if v is None else v.to_dict(skip_optional)

    def validate_dict(self, field_name: str, v):
        assert not self.required or v is not None
        assert type(v) == dict
        self.obj_type.validate_dict(v)

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

    def to_dict(self, v, skip_optional: bool = False):
        return [self.obj_type.to_dict(e, skip_optional) for e in v]

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

    def to_dict(self, v, skip_optional: bool = False):
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

    def to_dict(self, v, skip_optional: bool = False):
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


class DictValueField(Field):
    """
    Deprecated function. Use DictField instead
    """

    def __init__(self, value_type: Type[_BaseDictAble], required: bool = False, key: str = None):
        self.value_type = value_type
        super(DictValueField, self).__init__(required, key)

    def from_dict(self, v):
        return {key: self.value_type(dict=val) for key, val in v.items()}

    def to_dict(self, v, skip_optional: bool = False):
        return {key: val.to_dict(skip_optional) for key, val in v.items()}

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
        self.fields = fields

    def from_dict(self, v):
        for field in self.fields:
            try:
                field.validate_dict('', v)
                return field.from_dict(v)
            except (AssertionError, DataValidationError):
                pass
        raise NotImplementedError()

    def to_dict(self, v, skip_optional: bool = False):
        for field in self.fields:
            try:
                field.validate('', v)
                return field.to_dict(v, skip_optional)
            except AssertionError:
                pass
        raise NotImplementedError()

    def validate_dict(self, field_name: str, v):
        for field in self.fields:
            try:
                field.validate_dict('', v)
                return
            except (AssertionError, DataValidationError):
                pass
        raise AssertionError(f'{v} does not match for any of {[f.__class__.__name__ for f in self.fields]}')

    def validate(self, field_name: str, v):
        for field in self.fields:
            try:
                field.validate('', v)
                return
            except (AssertionError, DataValidationError) as e:
                pass
        raise AssertionError(f'{v} does not match for any of {[f.__class__.__name__ for f in self.fields]}')

    def of(self):
        return [field.spec() for field in self.fields]


class NoneField(Field):
    def from_dict(self, v):
        return None

    def to_dict(self, v, skip_optional: bool = False):
        return None

    def validate_dict(self, field_name: str, v):
        assert v is None

    def validate(self, field_name: str, v):
        assert v is None


class AnyField(Field):
    def from_dict(self, v):
        return v

    def to_dict(self, v, skip_optional: bool = False):
        return v

    def validate_dict(self, field_name: str, v):
        pass

    def validate(self, field_name: str, v):
        pass


class DictField(Field):
    def __init__(
            self,
            key_type: Field = AnyField(),
            value_type: Field = AnyField(),
            required: bool = False,
            key: str = None,
            default: Any = None,
            default_factory: DefaultFactoryType = None
    ):
        super(DictField, self).__init__(required=required, key=key, default=default, default_factory=default_factory)
        self.key_type = key_type
        self.value_type = value_type

    def from_dict(self, value):
        return {self.key_type.from_dict(k): self.value_type.from_dict(v) for k, v in value.items()}

    def to_dict(self, value, skip_optional: bool = False):
        return {self.key_type.to_dict(k, skip_optional): self.value_type.to_dict(v, skip_optional)
                for k, v in value.items()}

    def validate_dict(self, field_name: str, value):
        assert type(value) is dict
        for k, v in value.items():
            try:
                self.key_type.validate_dict(None, k)
            except AssertionError as e:
                raise DataValidationError(k, f'Invalid key, {str(e)}')
            except DataValidationError as e:
                raise DataValidationError(f'{k}.{e.path}', f'Invalid key, {str(e.err)}')

            try:
                self.value_type.validate_dict(None, v)
            except AssertionError as e:
                raise DataValidationError(k, f'Invalid value')
            except DataValidationError as e:
                raise DataValidationError(f'{k}.{e.path}', f'Invalid value, {str(e.err)}')

    def validate(self, field_name: str, value):
        assert type(value) is dict
        for k, v in value.items():
            self.key_type.validate(None, k)
            self.value_type.validate(None, v)
            
    def of(self):
        return {
            'key': self.key_type.spec(),
            'value': self.value_type.spec()
        }   
         

class RegexField(Field):
    def __init__(self, regex_string: str, *args, **kwargs):
        super(RegexField, self).__init__(*args, **kwargs)
        self.regex_string = regex_string

    def from_dict(self, v):
        return v

    def to_dict(self, v, skip_optional: bool = False):
        return v

    def validate_dict(self, field_name: str, v):
        assert isinstance(v, str)
        assert re.match(self.regex_string, v), f"{v} for {field_name} should be in proper format"

    def validate(self, field_name: str, v):
        assert isinstance(v, str)

    def of(self):
        return {'regex': self.regex_string}


class RangeIntField(Field):
    def __init__(self, min_val: int = 0, max_val: int = math.inf, *args, **kwargs):
        super(RangeIntField, self).__init__(*args, **kwargs)
        self.min_val = min_val
        self.max_val = max_val

    def from_dict(self, v):
        return v

    def to_dict(self, v, skip_optional: bool = False):
        return v

    def validate_dict(self, field_name: str, v):
        assert isinstance(v, int)
        assert self.min_val <= v <= self.max_val, \
            f"{v} for {field_name} should be in range {self.min_val} to {self.max_val}"

    def validate(self, field_name: str, v):
        assert isinstance(v, int)

    def of(self):
        return {'min': self.min_val, 'max': self.max_val}


class RangeFloatField(Field):
    def __init__(self, min_val: float = 0.0, max_val: float = math.inf, *args, **kwargs):
        super(RangeFloatField, self).__init__(*args, **kwargs)
        self.min_val = min_val
        self.max_val = max_val

    def from_dict(self, v):
        return v

    def to_dict(self, v, skip_optional: bool = False):
        return v

    def validate_dict(self, field_name: str, v):
        assert isinstance(v, float)
        assert self.min_val <= v <= self.max_val, \
            f"{v} for {field_name} should be in range {self.min_val} to {self.max_val}"

    def validate(self, field_name: str, v):
        assert isinstance(v, float)

    def of(self):
        return {'min': self.min_val, 'max': self.max_val}
