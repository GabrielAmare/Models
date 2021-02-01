from .BaseSerializer import BaseSerializer
from .IntSeriliazer import IntSerializer
from ..BaseModel import BaseModel


class ModelSeriliazer(BaseSerializer):
    @classmethod
    def serialize(cls, value, dtype=None, format=None):
        assert isinstance(value, dtype)
        return value.to_dict()

    @classmethod
    def deserialize(cls, value, dtype: type):
        assert issubclass(dtype, BaseModel)
        if isinstance(value, dtype):
            return value

        try:
            # try to acquire uid if specified
            _uid = value.get('uid') if isinstance(value, dict) else value
            uid = IntSerializer.deserialize(_uid)

            instance = dtype.__instances__.where(uid=uid).first

            if not instance:
                instance = dtype.load(uid=uid)

            # return the instance
            if not instance:
                return value

            if isinstance(value, dict):
                return dtype(**value)

            return instance
        except Exception as e:
            if isinstance(value, dict):
                # TODO : remove because it's unsafe to create automatically instances that way
                return dtype.from_dict(value)

        return super().deserialize(value, dtype)
