import inspect
from abc import abstractmethod
from typing import Dict


class Field:
    def __init__(self, required: bool = False, key: str = None):
        self.required = required
        self.key = key

    @abstractmethod
    def from_dict(self, v):
        pass

    @abstractmethod
    def to_dict(self, v):
        pass

    @abstractmethod
    def validate_dict(self, field_name: str, v):
        pass

    @abstractmethod
    def validate(self, field_name: str, v):
        pass


class DictAble:
    def __init__(self, *args, **kwargs):
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
    def __get_fields(cls) -> Dict[str, Field]:
        fields = {}
        for attr in inspect.getmembers(cls):
            if isinstance(attr[1], Field):
                fields[attr[0]] = attr[1]
        return fields

    @classmethod
    def __get_field_key(cls, obj_attr: str):
        field = cls.__get_fields()[obj_attr]
        return field.key if field.key else obj_attr

    def __clear_default_field_values(self):
        for attr, field in self.__class__.__get_fields().items():
            self.__setattr__(attr, None)

    def __apply_dict(self, d: dict):
        for attr, field in self.__class__.__get_fields().items():
            self.__setattr__(attr, field.from_dict(d.get(self.__get_field_key(attr))))

    def __validate_dict(self, raw_values: dict):
        for attr, field in self.__get_fields().items():
            value = raw_values.get(self.__get_field_key(attr))
            if value is None and not field.required:
                continue
            try:
                field.validate_dict(attr, value)
            except AssertionError:
                raise ValueError('Pre check failed. Invalid value {} for field {}'.format(value, attr))

    def __validate(self):
        for attr, field in self.__get_fields().items():
            value = self.__getattribute__(attr)
            if value is None and not field.required:
                continue
            try:
                field.validate(attr, value)
            except AssertionError:
                raise ValueError('Post check failed. Invalid value {} for field {}'.format(value, attr))

    def to_dict(self) -> dict:
        d = {}
        for attr, field in self.__class__.__get_fields().items():
            d[self.__get_field_key(attr)] = field.to_dict(self.__getattribute__(attr))
        return d

    @classmethod
    def get_input_spec(cls) -> dict:
        d = {}
        for attr, field in cls.__get_fields().items():
            d[cls.__get_field_key(attr)] = {
                'type': field.__class__.__name__,
                'required': field.required
            }
        return d
