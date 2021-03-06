""""""
import os
import sys
import shutil
import datetime

from models.utils import FileMgmt

from .errors import ModelCreateError, ModelUpdateError
from .utils import Query

from .BaseModel import BaseModel, DeleteMode, RequestMode
from .BaseRights import BaseRights
from .CRUD import CRUD
from .FORMATS import FORMATS


class Model(BaseModel, abstract=True, delete_mode=DeleteMode.ALLOW_HARD):
    debug = False

    @staticmethod
    def __build_database__():
        def flat(root: str, struct: dict):
            yield root
            for key, val in struct.items():
                for path in flat(key, val):
                    yield os.path.join(root, path)

        db_struct = Model.h.models.map(lambda model: (model.__name__, {"formats": {}})).dict()

        for path in flat(Model.__dbfp__, db_struct):
            if not os.path.exists(path):
                print(f"Model.__build_database__ : mkdir {path}")
                os.mkdir(path)

    @staticmethod
    def __build_formats__():
        def build_LAZY_format(model: type):
            assert issubclass(model, Model)
            format = {}
            for field in model.h.fields:
                if field.model:
                    l_format = dict(uid="int")
                else:
                    l_format = field.type_
                format[field.name] = l_format

            return format

        def build_EAGER_format(model: type):
            assert issubclass(model, Model)
            format = {}
            for field in model.h.fields:
                if field.model:
                    l_format = build_LAZY_format(model=field.model)
                else:
                    l_format = field.type_
                format[field.name] = l_format

            for foreign_key in model.h.foreign_keys:
                l_format = build_LAZY_format(model=foreign_key.model)
                format[foreign_key.name] = l_format

            return format

        for model in Model.h.models:
            FileMgmt.save_json(f"{Model.__dbfp__}/{model.__name__}/formats/eager.json", build_EAGER_format(model))
            FileMgmt.save_json(f"{Model.__dbfp__}/{model.__name__}/formats/lazy.json", build_LAZY_format(model))

    @classmethod
    def __load_format__(cls, format):
        try:
            return FileMgmt.load_json(f"{Model.__dbfp__}/{cls.__name__}/formats/{format}.json")
        except:
            return None

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

        if Model.__dbfp__:
            Model.__build_database__()
            Model.__build_formats__()

        if loadall:
            Model.loadall()

    @staticmethod
    def show_models():
        for model in Model.h.models:
            print(model.__rpy__())
            print()

    @staticmethod
    def show_instances():
        for model in Model.h.models:
            print(model.__name__ + ":")
            for instance in model.h.instances:
                print("   ", instance)
            print()

    @staticmethod
    def __build_routes__(api):
        for model in Model.h.models:
            model.__crud__.api.build_routes(api=api)

    @staticmethod
    def __create_backup__():
        """Create a backup for the entire database"""
        now = datetime.datetime.now()
        timecode = f"db_{now.year}_{now.month}_{now.day}_{now.hour}_{now.minute}_{now.second}_{now.microsecond}"
        new_dirpath = os.path.join(Model.__backupdir__, timecode)
        shutil.copytree(Model.__dbfp__, new_dirpath)

    __dbfp__: str = 'database'
    __backupdir__: str = 'backups'
    __db_errs__: bool = True
    __db_warns__: bool = True

    __rights__: BaseRights = None
    __crud__: CRUD = None
    __formats__: FORMATS = None

    d: dict

    @classmethod
    def __rpy__(cls):
        return f"{cls.__name__}:\n" + "\n".join(f"    {attribute.__rpy__()}" for attribute in cls.h.attributes)

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        cls.__crud__ = CRUD(model=cls)
        cls.__formats__ = FORMATS(model=cls)

    def __new__(cls, **config):
        uid = config.pop('uid', 0)
        instance = cls.h.get_instance(uid) if isinstance(uid, int) and uid > 0 else None
        return instance or super().__new__(cls)

    def __init__(self, **config):
        if hasattr(self, 'd'):
            self.__class__.__apply__(instance=self, config=config, create=False)
        else:
            self.d = {}
            self.__class__.__apply__(instance=self, config=config, create=True)
            self.h.add_instance(self)

    def __call__(self, **config):
        self.__class__.__apply__(instance=self, config=config, create=False)
        return self

    def __repr__(self):
        return self.__class__.__name__ + "(" + ", ".join(
            f"{key}={repr(val)}" for key, val in self.to_database().items()) + ")"

    @classmethod
    def __apply__(cls, instance, config: dict, create: bool, save: bool = False):
        """

        :param instance: The target instance
        :param config: The data to apply
        :param create: True -> create mode, False -> update mode
        :return: The target instance
        """
        assert isinstance(instance, cls)
        if 'uid' in config:
            if not create:
                assert instance.uid == config['uid']
                del config['uid']

        qfk = cls.h.foreign_keys.keep(lambda foreign_key: foreign_key.name in config).finalize(safe=True)

        # define context
        if create:
            q = cls.h.fields
            err_cls = ModelCreateError
        else:
            q = cls.h.fields.keep(lambda field: field.name in config).finalize(safe=True)
            err_cls = ModelUpdateError

        # extracting foreign keys
        data_fks = {}
        for name in qfk.getattr("name"):
            data_fks[name] = config.pop(name)

        # create data
        data = {}
        for name in q.getattr('name'):
            data[name] = config.pop(name, None)

        # check unparsed values
        if config:
            error = Exception(f"Remaining keys in config : " + ", ".join(map(repr, config.keys())))
            if cls.debug:
                print(error, file=sys.stderr)
            else:
                raise error

        # parse values
        q = q.map(lambda field: (field, field.parse(cls, instance, data[field.name]))).finalize(safe=True)

        # parse errors
        errors = q.smap(lambda field, value: field.check(cls, instance, value, create)).list()
        error = err_cls(cls, errors)

        # handle error
        if error:
            if cls.debug:
                print(error, file=sys.stderr)
            else:
                raise error

        # apply changes
        for field, value in q:
            field.set(instance, value)

        # handle fks
        for name, value in data_fks.items():
            foreign_key = cls.h.get_foreign_key(name)

            if foreign_key.multiple and hasattr(value, '__iter__'):
                values = value
            else:
                values = [value]

            for item in values:
                cfg = {foreign_key.get_by: instance}

                if isinstance(item, foreign_key.model):
                    cfg.update(uid=item.uid)
                elif isinstance(item, int):
                    cfg.update(uid=item)
                elif isinstance(item, dict):
                    cfg.update(item)
                else:
                    raise Exception(f"Unable to parse {item}")

                resource = foreign_key.model(**cfg)

                if save:
                    resource.save()

        if save:
            instance.save()

        # emit events
        instance.h.emit(uid=instance.uid, method="create" if create else "update", name="", value=instance)

        return instance

    @classmethod
    def from_dict(cls, config):
        # we remove the foreign keys from the config
        for foreign_key in cls.h.foreign_keys:
            if foreign_key.name in config:
                value = config.pop(foreign_key.name)

        return cls(**config)

    def to_dict(self, mode=RequestMode.LAZY, safe=False):
        config = {}
        for field in self.h.fields:
            if safe or not field.private:
                value = field.get(self)

                if isinstance(value, Model):
                    value = value.uid

                if value is not None:
                    config[field.name] = value

        for attribute in self.h.attributes.where(distant=True):
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
        data = self.to_database()
        self.__dbm__.save(data)
        return self

    @classmethod
    def load(cls, uid: int, force_reload: bool = False):
        if not force_reload:
            if instance := cls.h.get_instance(uid):
                return instance
        database_data = cls.__dbm__.read(uid)
        server_data = cls.from_database(database_data)
        return cls(**server_data)

    @classmethod
    def loadall(cls, force_reload: bool = False):
        if cls is Model:
            for model in Model.h.models.sorted(lambda model: model.__level__()):
                print(f'Loading : {model.__name__}')
                model.loadall()
        else:
            return [cls.load(uid, force_reload=force_reload) for uid in cls.__dbm__.listall()]

    @classmethod
    def saveall(cls):
        if cls is Model:
            for model in Model.h.models:
                model.saveall()
        else:
            for instance in cls.h.instances:
                instance.save()

    def delete(self, soft=False):
        self.__dbm__.delete(self.uid, soft=soft)

        if self in self.h.instances:
            self.h.instances.remove(self)

    @classmethod
    def restore(cls, uid: int):
        cls.__dbm__.restore(uid)

    @classmethod
    def reload_db(cls):
        return cls.loadall(force_reload=True)

    ####################################################################################################################
    # DATABASE SERIALIZING
    ####################################################################################################################

    def to_database(self) -> dict:
        result = {}
        for field in self.h.fields:
            value = field.get(self)
            value = field.to_database(value)
            if value is not None:
                result[field.name] = value
        return result

    @classmethod
    def from_database(cls, database_data: dict) -> dict:
        server_data = {}
        for field in cls.h.fields:
            database_value = database_data.get(field.name)
            server_value = field.from_database(database_value)
            server_data[field.name] = server_value
        return server_data

    ####################################################################################################################
    # SERVER SERIALIZING
    ####################################################################################################################

    @classmethod
    def to_server(cls, server_data: dict, mode=RequestMode.LAZY) -> dict:
        """Map a dict containing server typed data into a dict containing database typed data"""
        final_data = {}
        for attribute in cls.h.attributes:
            if not attribute.private:
                if not attribute.distant or attribute.on_lazy or mode == RequestMode.EAGER:
                    server_value = server_data.get(attribute.name)
                    client_value = attribute.to_server(server_value)
                    if client_value is not None:
                        final_data[attribute.name] = client_value
        return final_data

    @classmethod
    def from_server(cls, server_data: dict) -> dict:
        final_data = {}
        for field in cls.h.fields:
            client_value = server_data.get(field.name)
            server_value = field.from_server(client_value)
            if server_value is not None:
                final_data[field.name] = server_value
        return final_data

    ####################################################################################################################
    # CLIENT SERIALIZING
    ####################################################################################################################

    @classmethod
    def to_client(cls, server_data: dict, mode=RequestMode.LAZY) -> dict:
        """Map a dict containing server typed data into a dict containing database typed data"""
        client_data = {}
        for attribute in cls.h.attributes:
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
        for field in cls.h.fields:
            client_value = client_data.get(field.name)
            server_value = field.from_client(client_value)
            if server_value is not None:
                server_data[field.name] = server_value
        return server_data

    @classmethod
    def __level__(cls):
        return cls.h.fields.getattr('__level__').max(default=-1) + 1
