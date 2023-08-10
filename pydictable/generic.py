import inspect
from typing import Dict

from pydictable import Field, DictAble


class GenericDictAble(DictAble):
    @classmethod
    def clone(cls):
        class _DictAble(DictAble):
            pass

        fields = {}
        for attr in inspect.getmembers(cls):
            if isinstance(attr[1], Field):
                fields[attr[0]] = attr[1]

        for key, value in fields.items():
            setattr(_DictAble, key, value)

        return _DictAble

    @staticmethod
    def inject(*args, **kwargs) -> Dict[str, Field]:
        pass

    @classmethod
    def make(cls, *args, **kwargs):
        new = cls.clone()
        for key, field in cls.inject(*args, **kwargs).items():
            setattr(new, key, field)
        return new
