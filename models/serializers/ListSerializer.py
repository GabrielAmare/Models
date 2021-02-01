from .BaseSerializer import BaseSerializer


class ListSerializer(BaseSerializer):
    @classmethod
    def serialize(cls, value: list, dtype=list, format=None):
        assert isinstance(value, list)
        return value

    @classmethod
    def deserialize(cls, value, dtype=list) -> list:
        if isinstance(value, list):
            return value
        elif hasattr(value, '__iter__'):
            return list(value)
        else:
            return [value]
