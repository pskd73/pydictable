import inspect
from datetime import datetime
from enum import Enum
from itertools import chain
from typing import Dict, get_type_hints, Union

from pydictable.field import StrField, IntField, FloatField, BoolField, ListField, MultiTypeField, UnionField, \
    NoneField, ObjectField, DataValidationError, EnumField, DatetimeField
from pydictable.type import _BaseDictAble, Field

TYPE_TO_FIELD = {
    str: StrField,
    int: IntField,
    float: FloatField,
    bool: BoolField,
    type(None): NoneField,
    datetime: DatetimeField
}


class DictAble(_BaseDictAble):
    def __init__(self, *args, **kwargs):
        super(DictAble, self).__init__(*args, **kwargs)
        self.__clear_default_field_values()
        fields = self.__get_fields()
        for k, v in kwargs.items():
            if k in fields:
                self.__setattr__(k, v)
        if kwargs.get('dict'):
            self.__validate_dict(kwargs['dict'])
            self.__apply_dict(kwargs['dict'])
        if len(args) > 0:
            raise ReferenceError('Use kwargs to init DictAble')
        self.__validate()

    @classmethod
    def __get_field_by_type_hint(cls, type_hint):
        if type_hint in TYPE_TO_FIELD:
            return TYPE_TO_FIELD[type_hint](required=True)
        if '__origin__' in type_hint.__dict__ and type_hint.__origin__ == Union:
            sub_types = []
            for sub_type in type_hint.__args__:
                sub_types.append(cls.__get_field_by_type_hint(sub_type))
            return UnionField(sub_types, required=True)
        if '__origin__' in type_hint.__dict__ and type_hint.__origin__ == list:
            return ListField(cls.__get_field_by_type_hint(type_hint.__args__[0]), required=True)
        if issubclass(type_hint, _BaseDictAble):
            return ObjectField(type_hint, required=True)
        if issubclass(type_hint, Enum):
            return EnumField(type_hint, required=True, is_name=True)
        raise NotImplementedError(f'Unsupported type hint {type_hint}')

    @classmethod
    def __get_fields(cls) -> Dict[str, Field]:
        fields = {}
        for attr in inspect.getmembers(cls):
            if isinstance(attr[1], Field):
                fields[attr[0]] = attr[1]
        for name, th in get_type_hints(cls).items():
            if name not in fields:
                fields[name] = cls.__get_field_by_type_hint(th)
        return fields

    @classmethod
    def __get_field_key(cls, obj_attr: str):
        field = cls.__get_fields()[obj_attr]
        return field.key if field.key else obj_attr

    def __clear_default_field_values(self):
        for attr, field in self.__class__.__get_fields().items():
            self.__setattr__(attr, None)

    def __apply_dict(self, d: dict):
        _updated_attributes = []
        for attr, field in chain(self.__class__.__get_fields().items(), d.items()):
            if isinstance(field, Field):
                self.__setattr__(attr, field.from_dict(d.get(self.__get_field_key(attr), field.default)))
                _updated_attributes.append(self.__get_field_key(attr))
                continue
            if attr not in _updated_attributes:
                self.__setattr__(attr, field)

    def __validate_dict(self, raw_values: dict):
        for attr, field in self.__get_fields().items():
            value = raw_values.get(self.__get_field_key(attr), field.default)
            if value is None and not field.required:
                continue
            try:
                field.validate_dict(attr, value)
            except DataValidationError as e:
                raise DataValidationError(f'{attr}.{e.path}', e.err)
            except AssertionError as e:
                if len(e.args) > 0:
                    raise DataValidationError(attr, f'Pre check failed: {str(e)}')
                raise DataValidationError(attr, f'Pre check failed: Invalid value {value} for field {attr}')

    def __validate(self):
        for attr, field in self.__get_fields().items():
            value = self.__getattribute__(attr)
            if value is None and not field.required:
                continue
            try:
                field.validate(attr, value)
            except DataValidationError as e:
                raise DataValidationError(f'{attr}.{e.path}', e.err)
            except AssertionError:
                raise DataValidationError(attr,
                                          'Post check failed. Invalid value "{}" for field "{}"'.format(value, attr))

    def to_dict(self) -> dict:
        d = {}
        _updated_attributes = []
        for attr, field in chain(self.__class__.__get_fields().items(), self.__dict__.items()):
            if isinstance(field, Field):
                d[self.__get_field_key(attr)] = field.to_dict(self.__getattribute__(attr))
                _updated_attributes.append(attr)
                continue
            if attr not in _updated_attributes:
                d[attr] = field
        return d

    @classmethod
    def get_input_spec(cls) -> dict:
        d = {}
        for attr, field in cls.__get_fields().items():
            d[cls.__get_field_key(attr)] = field.spec()
        return d
