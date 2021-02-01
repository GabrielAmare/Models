import hashlib
from datetime import datetime, date
from .utils import Attribute
from .Model import Model
from .utils import Query
from .errors import FieldError, FieldUpdateError, FieldCreateError
from .FieldDescriptor import FieldDescriptor

from .serializers import *


class FieldService:
    @classmethod
    def as_model(cls, model, value) -> Model:
        """Given any `value`, try to cast it as a `model` instance"""
        if isinstance(value, int):
            instance = model.load(value)
        elif isinstance(value, str) and IntSerializer.regex.match(value):
            instance = model.load(int(value))
        elif isinstance(value, dict):
            instance = model.from_dict(value)
        elif isinstance(value, model):
            instance = value
        else:
            raise Exception(f"Can't serialize {value} to a {model.__name__} !")

        assert isinstance(instance, model)
        return instance

    @classmethod
    def as_uid(cls, model, value) -> int:
        """Given any `value`, try to cast it as a `uid` corresponding to a `model` instance"""
        if isinstance(value, int):
            uid = value
        elif isinstance(value, str) and IntSerializer.regex.match(value):
            uid = int(value)
        elif isinstance(value, model):
            uid = value.uid
        elif isinstance(value, dict):
            uid = cls.as_uid(model, value.get('uid'))
        else:
            raise Exception(f"Can't serialize {value} to a {model.__name__} uid !")

        assert isinstance(uid, int)
        return uid


class FieldSerializer(BaseSerializer):
    @classmethod
    def serialize(cls, value, dtype, format=None):
        assert isinstance(value, dtype), f"{value.__class__.__name__} not {dtype.__name__}"
        if dtype is datetime:
            return DateTimeSeriliazer.serialize(value)
        elif dtype is date:
            return DateSeriliazer.serialize(value)
        elif dtype is int:
            return IntSerializer.serialize(value)
        elif dtype is float:
            return FloatSerializer.serialize(value)
        elif dtype is bool:
            return BoolSerializer.serialize(value)
        elif issubclass(dtype, Model):
            return ModelSeriliazer.serialize(value, dtype, format)
        else:
            return value

    @classmethod
    def deserialize(cls, value, dtype):
        try:
            if dtype is datetime:
                return DateTimeSeriliazer.deserialize(value)
            elif dtype is date:
                return DateSeriliazer.deserialize(value)
            elif dtype is int:
                return IntSerializer.deserialize(value)
            elif dtype is float:
                return FloatSerializer.deserialize(value)
            elif dtype is bool:
                return BoolSerializer.deserialize(value)
            elif issubclass(dtype, Model):
                return ModelSeriliazer.deserialize(value, dtype)
            else:
                return value
        except:
            return value

    @staticmethod
    def parse_increment(model, name, start, step):
        return model.h.instances.getattr(name).max(default=start) + step

    @staticmethod
    def parse_default(model, default):
        if hasattr(default, '__call__'):
            return default(model)
        else:
            return default


class Field(Attribute):
    DATABASE = "DATABASE"
    SERVER = "SERVER"
    CLIENT = "CLIENT"

    distant = False

    encryptions = {
        'md5': hashlib.md5,
        'sha1': hashlib.sha1,
        'sha224': hashlib.sha224,
        'sha256': hashlib.sha256,
        'sha384': hashlib.sha384,
        'sha512': hashlib.sha512,
        'blake2b': hashlib.blake2b,
        'blake2s': hashlib.blake2s
    }

    @classmethod
    def rpy(cls, rpy: str, **config):
        """Allow user to create a field using a rpy formatted string"""
        fd = FieldDescriptor.from_rpy(rpy)
        return cls(
            name=fd.name,
            type_=fd.type,
            optional=fd.optional,
            multiple=fd.multiple,
            unique=fd.unique,
            private=fd.private,
            static=fd.static,
            **config
        )

    def __rpy__(self):
        return self.descriptor.to_rpy()

    def __init__(self, name: str, type_: str, optional: bool = False, multiple: bool = False, unique: bool = False,
                 values=None, increment=None, range=None, length=None, default=None, encrypt=None,
                 private: bool = False, static: bool = False):
        """

        :param type_: The type of the field value (expected as string)
        :param optional: if True, the field is not required
        :param multiple: if True, the field handle a list of values
        :param unique: if True, for a given table, the same value cannot appears twice
        :param values: if specified (list), it's the set of authorized values for the field
        :param increment: if specified (tuple of 2 elements, start & step) auto-increment the field value when unspecified
        :param range: [optional] set a range of authorized values (ex: (0, 1000) )
        :param length: [optional] set a range of autorized length for the values
        :param default: [optional] either a default value, or a default value function (takes the model as argument)
        :param private: if True, the field value is filter out from the result of the $.to_dict method
        """
        super().__init__(name)

        self.descriptor = FieldDescriptor(
            # BASE
            name=name,
            type=type_,
            optional=optional,
            multiple=multiple,
            unique=unique,
            private=private,
            static=static,
            # FIELD
            range=range,
            length=length,
            default=default,
            encrypt=encrypt
        )

        self.type_ = type_
        self.optional = optional
        self.multiple = multiple
        self.unique = unique
        self.private = private
        self.static = static

        self.range = range
        self.length = (length, length) if isinstance(length, int) else length
        self.default = default
        self.encrypt = encrypt
        self.values = values
        self.increment = increment

    ####################################################################################################################
    # METHODS
    ####################################################################################################################

    def get(self, instance):
        """
            Field getter when given an instance and a name
        :param instance: the instance to get the value from
        :return: the value associated with the field
        """
        return instance.d.get(self.name)

    def set(self, instance, value):
        """
            Field setter when given an instance, name and value
        :param instance: the instance to set the value at
        :param value: the value to be set
        :return: None
        """
        assert isinstance(instance, Model)
        instance.d[self.name] = value
        instance.h.emit(uid=instance.uid, method="set", name=self.name, value=value)

    def append(self, instance, item):
        """
            Field adder when given an instance and an item to add (only works when self.multiple)
        :param instance: The instance to add to
        :param value: The item to add
        :return: None
        """
        assert self.multiple
        assert isinstance(instance, Model)
        instance.d[self.name].append(item)
        instance.h.emit(uid=instance.uid, method="append", name=self.name, value=item)

    def remove(self, instance, item):
        """
            Field remover when given an instance and an item to add (only works when self.multiple)
        :param instance: The instance to remove from
        :param value: The item to frmove
        :return: None
        """
        assert self.multiple
        assert isinstance(instance, Model)
        instance.d[self.name].append(item)
        instance.h.emit(uid=instance.uid, method="remove", name=self.name, value=item)

    @property
    def model(self):
        """Works only when the field is connected to a Model subclass"""
        return Model.h.get_model(self.type_)

    @property
    def dtype(self):
        """Works on every fields, return the expected type of data"""
        return self.model or eval(self.type_)

    def parse(self, model, instance, value):
        return self.deserialize(value, model)

    def check(self, model, instance, value, create: bool) -> FieldError:
        config = dict(model=model, instance=instance, field=self, value=value, create=create)
        errors = self.descriptor.checks.call(**config).filter(None).list()
        err_cls = FieldCreateError if create else FieldUpdateError
        return err_cls(self, errors)

    ####################################################################################################################
    # SERIALIZATION
    ####################################################################################################################

    def _deserialize(self, value, model=None):
        """For a given value, try to return a parsed version corresponding to the field value format"""
        if value is None:
            if self.optional:
                return None

            if model:
                if self.increment:
                    return FieldSerializer.parse_increment(model, self.name, *self.increment)
                elif self.default is not None:
                    return FieldSerializer.parse_default(model, self.default)

        return FieldSerializer.deserialize(value, self.dtype)

    def deserialize(self, value, model=None):
        """Parse the `value` received to the expected value for the field"""
        func = lambda obj: self._deserialize(obj, model)

        if self.multiple:
            values = ListSerializer.deserialize(value)
            return Query(values).map(func).filter(None).list()
        else:
            return func(value)

    def _serialize(self, value, dtype, format=True):
        if value is None:
            return None
        else:
            return FieldSerializer.serialize(value, dtype, format)

    def serialize(self, value, format=True):
        if not format:
            return None

        dtype = self.dtype
        func = lambda obj: self._serialize(obj, dtype, format)

        if self.multiple:
            values = ListSerializer.serialize(value)
            return Query(values).map(func).filter(None).list() or None
        else:
            return func(value)

    ####################################################################################################################
    # DATABASE SERIALIZING
    ####################################################################################################################

    def from_database(self, data):
        # return self.deserialize(data)
        if self.model:
            if data is None:
                return None
            elif not self.multiple:
                return FieldService.as_model(self.model, data)
            elif hasattr(data, '__iter__'):
                return [FieldService.as_model(self.model, item) for item in data]
            else:
                raise Exception(f"Can't serialize {data} from database !")
        elif self.type_ == "datetime" and isinstance(data, str):
            return datetime.fromisoformat(data)
        elif self.type_ == "date" and isinstance(data, str):
            return date.fromisoformat(data)
        else:
            return data

    def to_database(self, data):
        # return self.serialize(data)
        if self.model:
            if data is None:
                return None
            elif not self.multiple:
                return FieldService.as_uid(self.model, data)
            elif hasattr(data, '__iter__'):
                return [FieldService.as_uid(self.model, item) for item in data if item is not None]
            else:
                raise Exception(f"Can't serialize {data} to database !")
        elif isinstance(data, datetime):
            return data.isoformat()
        elif isinstance(data, date):
            return data.isoformat()
        else:
            return data

    ####################################################################################################################
    # SERVER SERIALIZING
    ####################################################################################################################

    def from_server(self, data):
        if self.model:
            if data is None:
                return None
            elif not self.multiple:
                return FieldService.as_model(self.model, data)
            elif hasattr(data, '__iter__'):
                return [FieldService.as_model(self.model, item) for item in data]
            else:
                raise Exception(f"Can't serialize {data} from server !")
        elif self.type_ == "datetime" and isinstance(data, str):
            return datetime.fromisoformat(data)
        elif self.type_ == "date" and isinstance(data, str):
            return date.fromisoformat(data)
        elif self.encrypt:
            if isinstance(self.encrypt, str):
                if isinstance(data, str):
                    data = bytes(data, encoding="utf-8")
                m = Field.encryptions[self.encrypt]()
                m.update(data)
                return m.hexdigest()
            else:
                raise Exception(f"Can't encrypt {data} with {self.encrypt}")
        else:
            return data

    def to_server(self, data):
        if self.model:
            if data is None:
                return None
            elif not self.multiple:
                return FieldService.as_uid(self.model, data)
            elif hasattr(data, '__iter__'):
                return [FieldService.as_uid(self.model, item) for item in data if item is not None]
            else:
                raise Exception(f"Can't serialize {data} to server !")
        else:
            return data

    ####################################################################################################################
    # CLIENT SERIALIZING
    ####################################################################################################################

    def from_client(self, data):
        if self.model:
            if data is None:
                return None
            elif not self.multiple:
                return FieldService.as_model(self.model, data)
            elif hasattr(data, '__iter__'):
                return [FieldService.as_model(self.model, item) for item in data]
            else:
                raise Exception(f"Can't serialize {data} from client !")
        elif self.type_ == "datetime" and isinstance(data, str):
            return datetime.fromisoformat(data)
        elif self.type_ == "date" and isinstance(data, str):
            return date.fromisoformat(data)
        else:
            return data

    def to_client(self, data):
        if self.model:
            if data is None:
                return None
            elif not self.multiple:
                return FieldService.as_uid(self.model, data)
            elif hasattr(data, '__iter__'):
                return [FieldService.as_uid(self.model, item) for item in data if item is not None]
            else:
                raise Exception(f"Can't serialize {data} to client !")
        elif isinstance(data, datetime):
            return data.isoformat()
        elif isinstance(data, date):
            return data.isoformat()
        else:
            return data

    @property
    def __level__(self):
        if self.model:
            return self.model.__level__()
        else:
            return 0
