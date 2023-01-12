from abc import abstractmethod
from typing import Any


class Field:
    def __init__(self, required: bool = False, key: str = None, default: Any = None):
        self.required = required
        self.key = key
        self.default = default

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

    def of(self):
        return

    def spec(self) -> dict:
        spec = {
            'type': self.__class__.__name__,
            'required': self.required
        }
        of = self.of()
        if of:
            spec['of'] = of
        return spec


class _BaseDictAble:
    def __init__(self, *args, **kwargs):
        pass

    @abstractmethod
    def to_dict(self) -> dict:
        pass
