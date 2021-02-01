class BaseSerializer:
    @classmethod
    def serialize(cls, value, dtype, format=None):
        raise NotImplementedError

    @classmethod
    def deserialize(cls, value, dtype: type):
        raise Exception(f"{cls.__name__} unable to deserialize {value} [{value.__class__.__name__}] to {dtype.__name__}")
