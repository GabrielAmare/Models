import re
from datetime import datetime, date
from models.utils import Attribute
from .Model import Model

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


class Field(Attribute):
    DATABASE = "DATABASE"
    SERVER = "SERVER"
    CLIENT = "CLIENT"

    distant = False

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
        card = {
            (False, False): "!",
            (False, True): "+",
            (True, False): "?",
            (True, True): "*",
        }[(self.optional, self.multiple)]

        return f"{card}{self.name}[{self.type_}]"

    def __init__(self, name: str, type_: str, optional: bool = False, multiple: bool = False, unique: bool = False,
                 values=None, increment=None, range=None, length=None, default=None, private: bool = False):
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
        self.type_ = type_
        self.optional = optional
        self.multiple = multiple
        self.unique = unique
        self.values = values
        self.increment = increment
        self.range = range
        self.length = (length, length) if isinstance(length, int) else length
        self.default = default
        self.private = private

    def get(self, instance):
        """
            Field getter when given an instance and a name
        :param instance:
        :return:
        """
        return instance.__data__.get(self.name)

    def set(self, instance, value):
        """
            Field setter when given an instance, name and value
        :param instance:
        :param name:
        :param value:
        :return:
        """
        instance.__data__[self.name] = value
        instance.events.emit(f"{self.name}:set", instance, value)

    def append(self, instance, value):
        assert self.multiple
        instance.__data__[self.name].append(value)
        instance.events.emit(f"{self.name}:append", instance, value)

    def remove(self, instance, value):
        assert self.multiple
        instance.__data__[self.name].append(value)
        instance.events.emit(f"{self.name}:remove", instance, value)

    @property
    def model(self):
        """Works only when the field is connected to a Model subclass"""
        return Model.__get_model__(self.type_)

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
        elif self.model:  # parse as model instance
            return FieldParsing.parse_model(self.model, value)
        else:  # no parsing
            return value

    def check(self, modelOrInstance, value):
        model, instance = self.get_model_and_instance(modelOrInstance)

        errors = []
        if not self.optional:
            if self.multiple:
                if not value:
                    errors.append("At least 1 element required")
            else:
                if value is None:
                    errors.append("Value is not optional")

            if self.model:
                if not isinstance(value, self.model):
                    errors.append(f"The value {value} should be typed as {self.type_}")
            else:
                if not isinstance(value, eval(self.type_)):
                    errors.append(f"The value {value} should be typed as {self.type_}")

            if self.unique:
                if model.__instances__.where(**{self.name: value}).first not in (None, instance):
                    errors.append(f"Value already existing in the column : {value}")

            if self.values:
                if value not in self.values:
                    errors.append(f"The value {value} doesn't belong to the list of authorized values")

            if self.range:
                if not self.range[0] <= value <= self.range[1]:
                    errors.append(f"The value {value} doesn't belong to the range {self.range}")

            if self.length:
                if not self.length[0] <= len(value) <= self.length[1]:
                    errors.append(f"The value {value} doesn't belong to the range {self.range}")

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
