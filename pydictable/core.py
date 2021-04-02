import inspect
from abc import abstractmethod
from typing import Dict


class Field:
    def __init__(self, required: bool=False):
        self.required = required

    def validate(self, field_name: str, v):
        try:
            self.validate_value(field_name, v)
        except AssertionError:
            if self.required and v is None:
                raise ValueError('Invalid value {} for field {}'.format(v, field_name))

    @abstractmethod
    def from_json(self, v):
        pass

    @abstractmethod
    def to_json(self, v):
        pass

    @abstractmethod
    def validate_value(self, field_name: str, v):
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
            field.validate(attr, self.__getattribute__(attr))

    def to_json(self) -> dict:
        return {attr: field.to_json(self.__getattribute__(attr)) for attr, field in self.__get_fields(self).items()}
