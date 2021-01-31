import re
from datetime import datetime, date
from .utils import Attribute
from .Model import Model

from .FieldDescriptor import FieldDescriptor

regex_int = re.compile(r'^[0-9]+$')
regex_float = re.compile(r"^-?([0-9]+\.[0-9]*|\.[0-9]+|inf)$")


class FieldParsing:
    @staticmethod
    def parse_increment(model, name, start, step):
        return model.__instances__.getattr(name).max(default=start) + step

    @staticmethod
    def parse_int(value):
        if isinstance(value, int):
            return value
        elif isinstance(value, str) and regex_int.match(value):
            return int(value)
        else:
            return value

    @staticmethod
    def parse_float(value):
        if isinstance(value, float):
            return value
        elif isinstance(value, str) and regex_float.match(value):
            return int(value)
        else:
            return value

    @staticmethod
    def parse_bool(value):
        if isinstance(value, bool):
            return value
        elif isinstance(value, str) and value in ('True', 'true'):
            return True
        elif isinstance(value, str) and value in ('False', 'false'):
            return False
        else:
            return value

    @staticmethod
    def parse_default(model, default):
        if hasattr(default, '__call__'):
            return default(model)
        else:
            return default

    @staticmethod
    def parse_model(model, value):
        if isinstance(value, model):
            return value

        # try to acquire uid if specified
        if isinstance(value, int):  # get by uid
            uid = value
        elif isinstance(value, str) and regex_int.match(value):  # get by string uid
            uid = int(value)
        elif isinstance(value, dict):  # get by dict (or uid)
            uid = value.get('uid')
        else:
            uid = None

        # try to acquire instance if it exists or create if not
        if uid is None:
            if isinstance(value, dict):
                # TODO : remove because it's unsafe to create automatically instances that way
                return model.from_dict(value)
            else:
                return value

        instance = model.__instances__.where(uid=uid).first

        if not instance:
            instance = model.load(uid=uid)

        # return the instance
        if not instance:
            return value

        if isinstance(value, dict):
            instance.__update__(**value)

        return instance


import hashlib


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

    @staticmethod
    def get_model_and_instance(modelOrInstance):
        if type(modelOrInstance) is type:
            model = modelOrInstance
            instance = None
        else:
            model = modelOrInstance.__class__
            instance = modelOrInstance
        return model, instance

    def __rpy__(self):
        return self.__descriptor__.to_rpy()

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

        self.__descriptor__ = FieldDescriptor(
            # BASE
            name=name,
            type=type_,
            optional=optional,
            multiple=multiple,
            unique=unique,
            private=private,
            static=static,
            # ADDS
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

    @property
    def holds_model(self) -> bool:
        return bool(self.model)

    ####################################################################################################################
    # METHODS
    ####################################################################################################################

    def get(self, instance):
        """
            Field getter when given an instance and a name
        :param instance: the instance to get the value from
        :return: the value associated with the field
        """
        return instance.__data__.get(self.name)

    def set(self, instance, value):
        """
            Field setter when given an instance, name and value
        :param instance: the instance to set the value at
        :param value: the value to be set
        :return: None
        """
        instance.__data__[self.name] = value
        instance.__emit__(self.name, "set", value)

    def append(self, instance, item):
        """
            Field adder when given an instance and an item to add (only works when self.multiple)
        :param instance: The instance to add to
        :param value: The item to add
        :return: None
        """
        assert self.multiple
        instance.__data__[self.name].append(item)
        instance.__emit__(self.name, "append", item)

    def remove(self, instance, item):
        """
            Field remover when given an instance and an item to add (only works when self.multiple)
        :param instance: The instance to remove from
        :param value: The item to frmove
        :return: None
        """
        assert self.multiple
        instance.__data__[self.name].append(item)
        instance.__emit__(self.name, "remove", item)

    @property
    def model(self):
        """Works only when the field is connected to a Model subclass"""
        return Model.__get_model__(self.type_)

    @property
    def dtype(self):
        """Works on every fields, return the expected type of data"""
        return self.model or eval(self.type_)

    def parse(self, modelOrInstance, value):
        model, instance = self.get_model_and_instance(modelOrInstance)

        if value is None and self.increment:  # parse with auto-increment
            return FieldParsing.parse_increment(model, self.name, *self.increment)
        elif value is None and self.default is not None:  # parse with default value or function
            return FieldParsing.parse_default(model, self.default)
        elif self.type_ == "int":  # parse as integer
            return FieldParsing.parse_int(value)
        elif self.type_ == "float":  # parse as decimal
            return FieldParsing.parse_float(value)
        elif self.type_ == "bool":  # parse as boolean
            return FieldParsing.parse_bool(value)
        elif self.model:  # parse as model instance
            return FieldParsing.parse_model(self.model, value)
        else:  # no parsing
            return value

    def check(self, modelOrInstance, value, mode) -> list:
        assert mode in ('create', 'update')
        model, instance = self.get_model_and_instance(modelOrInstance)

        errors = []

        for check in self.__descriptor__.__checks__:
            if error := check(model=model, instance=instance, field=self, value=value, mode=mode):
                errors.append(error)

        return errors

    def uid_to_model(self, value):
        if isinstance(value, int):
            result = self.model.load(value)
        elif isinstance(value, str) and regex_int.match(value):
            result = self.model.load(int(value))
        elif isinstance(value, dict):
            result = self.model.from_dict(value)
        elif isinstance(value, self.model):
            result = value
        else:
            raise Exception(f"Can't serialize {value} to server !")
        assert isinstance(result, self.model)
        return result

    def model_to_uid(self, value) -> int:
        if isinstance(value, int):
            result = value
        elif isinstance(value, str) and regex_int.match(value):
            result = int(value)
        elif isinstance(value, self.model):
            result = value.uid
        elif isinstance(value, dict):
            return self.model_to_uid(value.get('uid'))
        else:
            raise Exception(f"Can't serialize {value} to database !")
        # assert isinstance(result, int)
        return result

    ####################################################################################################################
    # DATABASE SERIALIZING
    ####################################################################################################################

    def from_database(self, data):
        if self.model:
            if data is None:
                return None
            elif not self.multiple:
                return self.uid_to_model(data)
            elif hasattr(data, '__iter__'):
                return list(map(self.uid_to_model, data))
            else:
                raise Exception(f"Can't serialize {data} from database !")
        elif self.type_ == "datetime" and isinstance(data, str):
            return datetime.fromisoformat(data)
        elif self.type_ == "date" and isinstance(data, str):
            return date.fromisoformat(data)
        else:
            return data

    def to_database(self, data):
        if self.model:
            if data is None:
                return None
            elif not self.multiple:
                return self.model_to_uid(data)
            elif hasattr(data, '__iter__'):
                return [self.model_to_uid(item) for item in data if item is not None]
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
                return self.uid_to_model(data)
            elif hasattr(data, '__iter__'):
                return list(map(self.uid_to_model, data))
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
                return self.uid_to_model(data)
            elif hasattr(data, '__iter__'):
                return [self.uid_to_model(item) for item in data if item is not None]
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
                return self.uid_to_model(data)
            elif hasattr(data, '__iter__'):
                return list(map(self.uid_to_model, data))
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
                return self.model_to_uid(data)
            elif hasattr(data, '__iter__'):
                return [self.model_to_uid(item) for item in data if item is not None]
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
