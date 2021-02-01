from datetime import datetime

from .BaseSerializer import BaseSerializer


class DateTimeSeriliazer(BaseSerializer):
    @classmethod
    def serialize(cls, value: datetime, dtype=datetime, format=None):
        return value.isoformat()

    @classmethod
    def deserialize(cls, value, dtype=datetime) -> datetime:
        if isinstance(value, datetime):
            return value
        elif isinstance(value, str):
            return datetime.fromisoformat(value)

        return super().deserialize(value, dtype)
