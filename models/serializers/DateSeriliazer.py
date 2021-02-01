from datetime import date

from .BaseSerializer import BaseSerializer


class DateSeriliazer(BaseSerializer):
    @classmethod
    def serialize(cls, value: date, dtype=date, format=None):
        return value.isoformat()

    @classmethod
    def deserialize(cls, value, dtype=date) -> date:
        if isinstance(value, date):
            return value
        elif isinstance(value, str):
            return date.fromisoformat(value)

        return super().deserialize(value, dtype)