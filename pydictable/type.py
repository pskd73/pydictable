from abc import abstractmethod


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


class _BaseDictAble:
    def __init__(self, *args, **kwargs):
        pass

    @abstractmethod
    def to_dict(self) -> dict:
        pass
