from models.utils import Query, EventManager
from .DatabaseManager import DatabaseManager


class ModelOverwriteError(Exception):
    def __init__(self, old, new):
        self.old = old
        self.new = new

    def __repr__(self):
        return f"You're trying to redefine {self.old.__name__}, set param overwrite=True or name your model differently"


class InstanceAlreadyExistsError(Exception):
    def __init__(self, old, new):
        self.old = old
        self.new = new

    def __repr__(self):
        return f"You're trying to redefine {self.old.__class__.__name__}:{self.old.uid}, use __update__ method instead"


class DeleteMode:
    INHERIT = "INHERIT"
    SOFT = "SOFT"
    HARD = "HARD"
    ALLOW_HARD = "ALLOW_HARD"
    ALLOW_SOFT = "ALLOW_SOFT"


class RequestMode:
    LAZY = "LAZY"
    EAGER = "EAGER"


class BaseModel:
    """
        __models__ <-> Tables
        __attributes__ <-> Columns
        __instances__ <-> Rows

        __delete_mode__ :
            INHERIT    => inherit deletion mode from super
            SOFT       => force soft delete
            HARD       => force hard delete
            ALLOW_HARD => soft delete by default but allow hard delete
            ALLOW_SOFT => hard delete by default but allow soft delete
    """
    __models__: Query = Query(safe=True)

    __attributes__: Query = Query(safe=True)
    __instances__: Query = Query(safe=True)

    __dbm__: DatabaseManager
    __delete_mode__ = DeleteMode.ALLOW_HARD

    events = EventManager()

    @classmethod
    def __on_delete__(cls, mode=None):
        root_mode = cls.__get_delete_mode__()
        if mode is None:
            if root_mode in [DeleteMode.HARD, DeleteMode.ALLOW_SOFT]:
                return DeleteMode.HARD
            elif root_mode in [DeleteMode.SOFT, DeleteMode.ALLOW_HARD]:
                return DeleteMode.SOFT
            else:
                raise Exception(f"{cls.__name__}.__on_delete__(mode={mode}) but root mode is {root_mode}")
        elif mode == DeleteMode.HARD:
            if root_mode in [DeleteMode.HARD, DeleteMode.ALLOW_HARD, DeleteMode.ALLOW_SOFT]:
                return DeleteMode.HARD
            else:
                raise Exception(f"Hard Delete Mode is not allowed by {cls.__name__} -> {root_mode}")
        elif mode == DeleteMode.SOFT:
            if root_mode in [DeleteMode.SOFT, DeleteMode.ALLOW_SOFT, DeleteMode.ALLOW_HARD]:
                return DeleteMode.SOFT
            else:
                raise Exception(f"Soft Delete Mode is not allowed by {cls.__name__} -> {root_mode}")
        else:
            raise Exception

    @classmethod
    def __get_delete_mode__(cls):
        if cls.__delete_mode__ == DeleteMode.INHERIT:
            for super_cls in cls.__mro__:
                if super_cls is not cls:
                    if issubclass(super_cls, BaseModel):
                        return super_cls.__get_delete_mode__()
        elif cls.__delete_mode__ in [DeleteMode.HARD, DeleteMode.SOFT, DeleteMode.ALLOW_HARD, DeleteMode.ALLOW_SOFT]:
            return cls.__delete_mode__
        else:
            raise Exception(f"Invalid DeleteMode for {cls.__name__} : {cls.__delete_mode__}")

    def __init_subclass__(cls, abstract=False, **kwargs):
        cls.__dbm__ = DatabaseManager(cls)

        cls.__delete_mode__ = kwargs.get('delete_mode', DeleteMode.INHERIT)

        # register the Model subclass into the subclasses and create their Database folder
        if not abstract:
            cls.__add_model__(cls)
            if not cls.__dbm__.exists():
                cls.__dbm__.mkdir()

        cls.__attributes__ = Query(safe=True)
        cls.__inherit_attributes__()

        cls.__instances__ = Query(safe=True)
        cls.events = EventManager(piped=BaseModel.events)

    def __getattribute__(self, name: str):
        if name.startswith('__') and name.endswith('__'):
            return super().__getattribute__(name)
        elif attribute := self.__get_attribute__(name):
            return attribute.get(self)
        else:
            return super().__getattribute__(name)

    def __setattr__(self, name, value):
        if attribute := self.__get_attribute__(name):
            attribute.set(self, value)
        else:
            super().__setattr__(name, value)

    ####################################################################################################################
    # __MODELS__
    ####################################################################################################################

    @staticmethod
    def __get_model__(name):
        return BaseModel.__models__.where(__name__=name).first

    @staticmethod
    def __add_model__(model, overwrite: bool = False):
        if old := BaseModel.__get_model__(model.__name__):
            if overwrite:
                BaseModel.__models__.replace(old, model)
            else:
                raise ModelOverwriteError(old=old, new=model)
        else:
            BaseModel.__models__.append(model)

    ####################################################################################################################
    # __ATTRIBUTES__
    ####################################################################################################################

    @classmethod
    def __inherit_attributes__(cls):
        for model in reversed(cls.__mro__):
            if model is BaseModel or issubclass(model, BaseModel):
                for attribute in model.__attributes__:
                    cls.__add_attribute__(attribute)

    @classmethod
    def __get_attribute__(cls, name):
        return cls.__attributes__.where(name=name).first

    @classmethod
    def __add_attribute__(cls, attribute):
        if old := cls.__get_attribute__(attribute.name):
            cls.__attributes__.replace(old, attribute)
        else:
            cls.__attributes__.append(attribute)

    ####################################################################################################################
    # __INSTANCES__
    ####################################################################################################################

    @classmethod
    def __get_instance__(cls, uid):
        return cls.__instances__.where(uid=uid).first

    @classmethod
    def __add_instance__(cls, instance):
        if old := cls.__get_instance__(instance.uid):
            raise InstanceAlreadyExistsError(old=old, new=instance)
        else:
            cls.__instances__.append(instance)

    @classmethod
    def __del_instance__(cls, instance):
        assert isinstance(instance, cls)
        cls.__instances__.remove(instance)
        del instance
