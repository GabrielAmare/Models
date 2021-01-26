""""""
import os
import sys
import shutil
import datetime
from models.utils import ConfigError, EventManager, Query

from .BaseModel import BaseModel, DeleteMode, RequestMode
from .BaseRights import BaseRights
from .CRUD import CRUD
from .API import API


def lock(method):
    """
        This method locks itself on the first call, this can handle only 1 method by class
        if multiple methods are locks, the first one to be calle will lock the other ones
    """

    def locked_method(self, *args, **kwargs):
        if not hasattr(self, '_lock'):
            self._lock = True
            method(self, *args, **kwargs)

    return locked_method


class Model(BaseModel, abstract=True, delete_mode=DeleteMode.ALLOW_HARD):
    debug = False

    @staticmethod
    def setup(__dbfp__=None, __backupdir__=None, __db_errs__=None, __db_warns__=None, loadall=False):
        if __dbfp__ is not None:
            Model.__dbfp__ = str(__dbfp__)

        if __backupdir__ is not None:
            Model.__backupdir__ = str(__backupdir__)

        if __db_errs__ is not None:
            Model.__db_errs__ = bool(__db_errs__)

        if __db_warns__ is not None:
            Model.__db_warns__ = bool(__db_warns__)

        if loadall:
            Model.loadall()

    @staticmethod
    def show_models():
        for model in Model.__models__:
            print(model.__rpy__())
            print()

    @staticmethod
    def show_instances():
        for model in Model.__models__:
            print(model.__name__ + ":")
            for instance in model.__instances__:
                print("   ", instance)
            print()

    __dbfp__: str = 'database'
    __backupdir__: str = 'backups'
    __db_errs__: bool = True
    __db_warns__: bool = True

    __rights__: BaseRights = None
    __crud__: CRUD = None
    __api__: API = None

    __data__: dict

    @classmethod
    def __rpy__(cls):
        return f"{cls.__name__}:\n" + "\n".join(f"    {attribute.__rpy__()}" for attribute in cls.__attributes__)

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.__crud__ = CRUD(model=cls)
        cls.__api__ = API(model=cls)

    def __new__(cls, **config):
        if (uid := config.get('uid')) is not None:
            if instance := cls.__get_instance__(uid):
                instance.__update__(**config)
                return instance
        return super().__new__(cls)

    @lock
    def __init__(self, **config):
        self.__data__ = {}

        self.__create__(**config)

        self.events = EventManager(piped=self.__class__.events)
        self.__add_instance__(self)

    @staticmethod
    def __build_routes__(api):
        for model in Model.__models__:
            model.__api__.build_routes(api=api)

    ####################################################################################################################
    # CREATE
    ####################################################################################################################

    def __create_configs__(self, config):
        config_errors = {}
        parsed_config = {}
        # TODO : check this part with the new attribute class (maybe check when it needs to be set or not)
        for attribute in self.__attributes__.where(distant=False):
            value = config.get(attribute.name)

            parsed_value = attribute.parse(self, value)
            field_errors = attribute.check(self, parsed_value)

            parsed_config[attribute.name] = parsed_value
            config_errors[attribute.name] = field_errors

        return parsed_config, config_errors

    def __create_errors__(self, config_errors):
        if any(field_errors for field_errors in config_errors.values()):
            error = ConfigError(self.__class__, config_errors)
            if self.__class__.debug:
                print(error, file=sys.stderr)
            else:
                raise error

    def __create_apply__(self, parsed_config):
        for name, value in parsed_config.items():
            if attribute := self.__attributes__.where(name=name, distant=False).first:
                attribute.set(self, value)

    def __create__(self, **config):
        parsed_config, config_errors = self.__create_configs__(config)

        self.__create_errors__(config_errors)

        self.__create_apply__(parsed_config)

    ####################################################################################################################
    # UPDATE
    ####################################################################################################################

    def __update_configs__(self, config):
        config_errors = {}
        parsed_config = {}
        # TODO : check this part with the new attribute class (maybe check when it needs to be set or not)
        for name, value in config.items():
            if (attribute := self.__get_attribute__(name)) and not attribute.distant:
                parsed_value = attribute.parse(self, value)
                field_errors = attribute.check(self, parsed_value)

                parsed_config[attribute.name] = parsed_value
                config_errors[attribute.name] = field_errors

        return parsed_config, config_errors

    def __update_errors__(self, config_errors):
        if any(field_errors for field_errors in config_errors.values()):
            error = ConfigError(self.__class__, config_errors)
            if self.__class__.debug:
                print(error, file=sys.stderr)
            else:
                raise error

    def __update_apply__(self, parsed_config):
        for name, value in parsed_config.items():
            if attribute := self.__attributes__.where(name=name, distant=False).first:
                attribute.set(self, value)

    def __update__(self, **config):
        parsed_config, config_errors = self.__update_configs__(config)

        self.__update_errors__(config_errors)

        self.__update_apply__(parsed_config)

        return self

    def __repr__(self):
        return self.__class__.__name__ + "(" + ", ".join(
            f"{key}={repr(val)}" for key, val in self.to_database(self.__data__).items()) + ")"

    @classmethod
    def from_dict(cls, config):
        return cls(**config)

    def to_dict(self, mode=RequestMode.LAZY, safe=False):
        config = {}
        for attribute in self.__attributes__.where(distant=False):
            if safe or not attribute.private:
                value = attribute.get(self)

                if isinstance(value, Model):
                    value = value.uid

                if value is not None:
                    config[attribute.name] = value

        for attribute in self.__attributes__.where(distant=True):
            if attribute.on_lazy or mode == RequestMode.EAGER:
                value = attribute.get(self)
                if isinstance(value, Query):
                    value = [obj.to_dict(mode=RequestMode.LAZY) for obj in value]
                elif isinstance(value, Model):
                    value = value.to_dict(mode=RequestMode.LAZY)

                if value:
                    config[attribute.name] = value

        return config

    ###################################################################################
    # SERVER <-> DATABASE (using DatabaseManager)
    ###################################################################################

    def save(self):
        server_data = self.to_dict(mode=RequestMode.LAZY, safe=True)
        database_data = self.to_database(server_data)
        self.__dbm__.save(database_data)
        return self

    @classmethod
    def load(cls, uid: int, force_reload: bool = False):
        if not force_reload:
            if instance := cls.__instances__.where(uid=uid).first:
                return instance
        database_data = cls.__dbm__.read(uid)
        server_data = cls.from_database(database_data)
        return cls.from_dict(server_data)

    @classmethod
    def loadall(cls, force_reload: bool = False):
        if cls is Model:
            for model in Model.__models__.sorted(lambda model: model.__level__()):
                print(f'Loading : {model.__name__}')
                model.loadall()
        else:
            return [cls.load(uid, force_reload=force_reload) for uid in cls.__dbm__.listall()]

    @classmethod
    def saveall(cls):
        if cls is Model:
            for model in Model.__models__:
                model.saveall()
        else:
            for instance in cls.__instances__:
                instance.save()

    def delete(self, soft=False):
        self.__dbm__.delete(self.uid, soft=soft)

        if self in self.__class__.__instances__:
            self.__class__.__instances__.remove(self)

    @classmethod
    def restore(cls, uid: int):
        cls.__dbm__.restore(uid)

    @staticmethod
    def __create_backup__():
        """Create a backup for the entire database"""
        now = datetime.datetime.now()
        timecode = f"db_{now.year}_{now.month}_{now.day}_{now.hour}_{now.minute}_{now.second}_{now.microsecond}"
        new_dirpath = os.path.join(Model.__backupdir__, timecode)
        shutil.copytree(Model.__dbfp__, new_dirpath)

    @classmethod
    def reload_db(cls):
        return cls.loadall(force_reload=True)

    ####################################################################################################################
    # DATABASE SERIALIZING
    ####################################################################################################################

    @classmethod
    def to_database(cls, server_data: dict) -> dict:
        """Map a dict containing server typed data into a dict containing database typed data"""
        database_data = {}
        for attribute in cls.__attributes__.where(distant=False):
            server_value = server_data.get(attribute.name)
            database_value = attribute.to_database(server_value)
            if database_value is not None:
                database_data[attribute.name] = database_value
        return database_data

    @classmethod
    def from_database(cls, database_data: dict) -> dict:
        server_data = {}
        for attribute in cls.__attributes__.where(distant=False):
            database_value = database_data.get(attribute.name)
            server_value = attribute.from_database(database_value)
            if server_value is not None:
                server_data[attribute.name] = server_value
        return server_data

    ####################################################################################################################
    # CLIENT SERIALIZING
    ####################################################################################################################

    @classmethod
    def to_client(cls, server_data: dict, mode=RequestMode.LAZY) -> dict:
        """Map a dict containing server typed data into a dict containing database typed data"""
        client_data = {}
        for attribute in cls.__attributes__:
            if not attribute.private:
                if not attribute.distant or attribute.on_lazy or mode == RequestMode.EAGER:
                    server_value = server_data.get(attribute.name)
                    client_value = attribute.to_client(server_value)
                    if client_value is not None:
                        client_data[attribute.name] = client_value
        return client_data

    @classmethod
    def from_client(cls, client_data: dict) -> dict:
        server_data = {}
        for attribute in cls.__attributes__.where(distant=False):
            client_value = client_data.get(attribute.name)
            server_value = attribute.from_client(client_value)
            if server_value is not None:
                server_data[attribute.name] = server_value
        return server_data

    @classmethod
    def __level__(cls):
        return cls.__attributes__.where(distant=False).getattr('__level__').max(default=-1) + 1
