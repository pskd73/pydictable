from abc import abstractmethod
from typing import Any, Callable, Tuple

DefaultFactoryType = Tuple[Callable, Tuple[Any], dict]


class Field:
    def __init__(
            self,
            required: bool = False,
            key: str = None,
            default: Any = None,
            default_factory: DefaultFactoryType = None,
    ):
        self.required = required
        self.key = key
        self.default = default
        self.default_factory = default_factory

    @abstractmethod
    def from_dict(self, v):
        pass

    @abstractmethod
    def to_dict(self, v, skip_optional: bool = False):
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
    def to_dict(self, skip_optional: bool = False) -> dict:
        pass

    @classmethod
    def validate_dict(cls, raw_values: dict):
        pass

    @classmethod
    def get_input_spec(cls):
        pass
