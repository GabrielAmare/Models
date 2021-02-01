import re

from .BaseSerializer import BaseSerializer


class FloatSerializer(BaseSerializer):
    regex = re.compile(r"^-?([0-9]+\.[0-9]*|\.[0-9]+|inf)$")

    @classmethod
    def serialize(cls, value: float, dtype=float, format=None):
        return value

    @classmethod
    def deserialize(cls, value, dtype=float) -> float:
        if isinstance(value, float):
            return value
        elif isinstance(value, str) and cls.regex.match(value):
            return float(value)

        return super().deserialize(value, dtype)