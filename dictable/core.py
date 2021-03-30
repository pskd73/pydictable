from abc import abstractmethod
from typing import List

PRIMITIVE_TYPES = [int, str, float, bool]


class Field:
    @abstractmethod
    def get_type(self):
        pass


class StringField(Field):
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
        if len(args) > 0:
            self.__apply_dict(self, args[0])

    @staticmethod
    def __apply_dict(obj, d: dict):
        obj_cls = obj.__class__
        for attr in dir(obj_cls):
            if attr in d:
                field: Field = obj_cls.__getattribute__(obj, attr)
                if field.get_type() in PRIMITIVE_TYPES:
                    obj.__setattr__(attr, d[attr])
                elif isinstance(field, ListField):
                    tmp_list = []
                    for e in d[attr]:
                        sub_obj = field.obj_type()
                        DictAble.__apply_dict(sub_obj, e)
                        tmp_list.append(sub_obj)
                    obj.__setattr__(attr, tmp_list)
                elif isinstance(field, ObjectField):
                    sub_obj = field.get_type()()
                    obj.__setattr__(attr, sub_obj)
                    DictAble.__apply_dict(sub_obj, d[attr])

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
