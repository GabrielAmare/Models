from .utils import Query, EventManager, ModelHandler
from .DatabaseManager import DatabaseManager


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
    __dbm__: DatabaseManager
    __delete_mode__ = DeleteMode.ALLOW_HARD

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
            ModelHandler.add_model(cls)

        cls.h = ModelHandler(cls)

        # inheritance
        for mro in reversed(cls.__mro__):
            if issubclass(mro, BaseModel):
                for attribute in mro.h.attributes:
                    cls.h.add_attribute(attribute)

        cls.__attributes__ = cls.h.attributes  # deprecated
        cls.__fields__ = cls.h.fields  # deprecated
        cls.__foreign_keys__ = cls.h.foreign_keys  # deprecated
        cls.__methods__ = cls.h.methods  # deprecated
        cls.__instances__ = cls.h.instances  # deprecated
        cls.__get_attribute__ = cls.h.get_attribute  # deprecated
        cls.__add_attribute__ = cls.h.add_attribute  # deprecated
        cls.__get_instance__ = cls.h.get_instance  # deprecated
        cls.__add_instance__ = cls.h.add_instance  # deprecated
        cls.__del_instance__ = cls.h.del_instance  # deprecated

    def __getattribute__(self, name: str):
        if name.startswith('__') and name.endswith('__') or name in ['h']:
            return super().__getattribute__(name)
        elif attribute := self.h.get_attribute(name):
            return attribute.get(self)
        else:
            return super().__getattribute__(name)

    def __setattr__(self, name, value):
        if attribute := self.h.get_attribute(name):
            attribute.set(self, value)
        else:
            super().__setattr__(name, value)


ModelHandler.base_model = BaseModel

BaseModel.h = ModelHandler(BaseModel)
BaseModel.__models__ = ModelHandler.models  # deprecated
BaseModel.__get_model__ = ModelHandler.get_model  # deprecated
BaseModel.__add_model__ = ModelHandler.add_model  # deprecated

BaseModel.__attributes__ = BaseModel.h.attributes  # deprecated
BaseModel.__instances__ = BaseModel.h.instances  # deprecated
BaseModel.__fields__ = BaseModel.h.fields  # deprecated
BaseModel.__foreign_keys__ = BaseModel.h.foreign_keys  # deprecated
BaseModel.__methods__ = BaseModel.h.methods  # deprecated
