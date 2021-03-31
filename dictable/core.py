import inspect
from abc import abstractmethod
from typing import List, Dict

PRIMITIVE_TYPES = [int, str, float, bool]


class Field:
    @abstractmethod
    def get_type(self):
        pass


class StrField(Field):
    def get_type(self):
        return str


class IntField(Field):
    def get_type(self):
        return int


class ObjectField(Field):
    def __init__(self, obj_type):
        self.obj_type = obj_type

    def get_type(self):
        return self.obj_type


class ListField(Field):
    def __init__(self, obj_type):
        self.obj_type = obj_type

    def get_type(self):
        return list


class DictAble:
    def __init__(self, *args, **kwargs):
        self.__apply_dict(self, {})
        if len(args) > 0:
            self.__apply_dict(self, args[0])

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
            obj.__setattr__(attr, DictAble.__get_field_value(field, d.get(attr)))

    @staticmethod
    def __get_field_value(field: Field, v):
        if v is None:
            return None
        if field.get_type() in PRIMITIVE_TYPES:
            return v
        if isinstance(field, ListField):
            tmp_list = []
            for e in v:
                tmp_list.append(DictAble.__get_field_value(field.obj_type, e))
            return tmp_list
        if isinstance(field, ObjectField):
            return field.get_type()(v)

    @staticmethod
    def __to_json(v):
        if type(v) in PRIMITIVE_TYPES:
            return v
        if isinstance(v, DictAble):
            return v.to_json()
        if type(v) is dict:
            ret = {}
            for k, v in v.items():
                ret[k] = DictAble.__to_json(v)
            return ret
        if type(v) is list:
            ret = []
            for e in v:
                ret.append(DictAble.__to_json(e))
            return ret
        raise NotImplementedError()

    def to_json(self) -> dict:
        return self.__to_json(self.__dict__)
