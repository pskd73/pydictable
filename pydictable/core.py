import inspect
from abc import abstractmethod
from typing import Dict


class Field:
    def __init__(self, required: bool=False, attr_name: str=None):
        self.required = required
        self.attr_name = attr_name

    def validate(self, field_name: str, v):
        try:
            self.validate_value(field_name, v)
        except AssertionError:
            if self.required and v is None:
                raise ValueError('Invalid value {} for field {}'.format(v, field_name))

    @abstractmethod
    def from_dict(self, v):
        pass

    @abstractmethod
    def to_dict(self, v):
        pass

    @abstractmethod
    def validate_value(self, field_name: str, v):
        pass


class DictAble:
    def __init__(self, *args, **kwargs):
        self.__fields = self.__get_fields()
        self.__clear_default_field_values()
        for k, v in kwargs.items():
            if k in self.__get_fields():
                self.__setattr__(k, v)
        if kwargs.get('dict'):
            self.__apply_dict(kwargs['dict'])
        if len(args) > 0:
            raise ReferenceError('Use kwargs to init DictAble')
        self.__validate()

    def __get_fields(self) -> Dict[str, Field]:
        fields = {}
        for attr in inspect.getmembers(self.__class__):
            if isinstance(attr[1], Field):
                fields[attr[0]] = attr[1]
        return fields

    def __get_attr_name(self, obj_attr: str):
        field = self.__fields[obj_attr]
        return field.attr_name if field.attr_name else obj_attr

    def __clear_default_field_values(self):
        for attr, field in self.__fields.items():
            self.__setattr__(attr, None)

    def __apply_dict(self, d: dict):
        for attr, field in self.__fields.items():
            self.__setattr__(attr, field.from_dict(d.get(self.__get_attr_name(attr))))

    def __validate(self):
        for attr, field in DictAble.__get_fields(self).items():
            field.validate(attr, self.__getattribute__(attr))

    def to_dict(self) -> dict:
        d = {}
        for attr, field in self.__fields.items():
            d[self.__get_attr_name(attr)] = field.to_dict(self.__getattribute__(attr))
        return d
