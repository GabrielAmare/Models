from .BaseSerializer import BaseSerializer


class BoolSerializer(BaseSerializer):
    @classmethod
    def serialize(cls, value: bool, dtype=bool, format=None):
        return value

    @classmethod
    def deserialize(cls, value, dtype=bool) -> bool:
        if isinstance(value, bool):
            return value
        elif isinstance(value, str):
            if value in ('True', 'true', '1'):
                return True
            elif value in ('False', 'false', '0'):
                return False

        return super().deserialize(value, dtype)