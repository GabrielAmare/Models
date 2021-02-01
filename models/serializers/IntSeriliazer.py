import re

from .BaseSerializer import BaseSerializer


class IntSerializer(BaseSerializer):
    regex = re.compile(r'^[0-9]+$')

    @classmethod
    def serialize(cls, value: int, dtype=int, format=None):
        return value

    @classmethod
    def deserialize(cls, value, dtype=int) -> int:
        if isinstance(value, int):
            return value
        elif isinstance(value, str) and cls.regex.match(value):
            return int(value)

        return super().deserialize(value, dtype)
