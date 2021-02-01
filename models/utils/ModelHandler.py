from .Query import Query
from .EventManager import EventManager


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


class ModelHandler:
    models: Query = Query(safe=True)
    events = EventManager

    attributes: Query
    field: Query
    foreign_keys: Query
    methods: Query
    instance: Query

    base_model = None

    def __init__(self, model=None):
        """
            Handle the attributes, fields, foreign keys, methods and instances for the `model`
        :param model: The model that
        """
        self.model = model

        self.attributes = Query(safe=True)

        self.fields = self.attributes.keeptype("Field").safe()
        self.foreign_keys = self.attributes.keeptype("ForeignKey").safe()
        self.methods = self.attributes.keeptype("Method").safe()

        self.instances = Query(safe=True)

    ####################################################################################################################
    # MODELS
    ####################################################################################################################

    @classmethod
    def get_model(cls, name: str):
        return cls.models.where(__name__=name).first

    @classmethod
    def add_model(cls, model, overwrite: bool = False):
        if old := cls.get_model(model.__name__):
            if overwrite:
                cls.models.replace(old, model)
            else:
                raise ModelOverwriteError(old=old, new=model)
        else:
            cls.models.append(model)

    ####################################################################################################################
    # INSTANCES
    ####################################################################################################################

    def get_instance(self, uid: int):
        return self.instances.where(uid=uid).first

    def add_instance(self, instance):
        if old := self.get_instance(instance.uid):
            raise InstanceAlreadyExistsError(old=old, new=instance)
        else:
            self.instances.append(instance)

    def del_instance(self, instance):
        assert isinstance(instance, self.model)
        self.instances.remove(instance)
        del instance

    ####################################################################################################################
    # ATTRIBUTES
    ####################################################################################################################

    def get_attribute(self, name: str):
        return self.attributes.where(name=name).first

    def add_attribute(self, attribute):
        if old := self.get_attribute(attribute.name):
            self.attributes.replace(old, attribute)
        else:
            self.attributes.append(attribute)

    ####################################################################################################################
    # FIELDS
    ####################################################################################################################

    def get_field(self, name: str):
        return self.fields.where(name=name).first

    ####################################################################################################################
    # FOREIGN KEYS
    ####################################################################################################################

    def get_foreign_key(self, name: str):
        return self.foreign_keys.where(name=name).first

    ####################################################################################################################
    # METHODS
    ####################################################################################################################

    def get_method(self, name: str):
        return self.methods.where(name=name).first

    ####################################################################################################################
    # EVENTS
    ####################################################################################################################

    def event(self, uid, method, name):
        return f"{self.model.__name__}/{uid}/{method}/{name}"

    def emit(self, uid, method, name, value):
        event = self.event(uid, method, name)
        return self.events.emit(event, value)

    def on(self, uid, method, name, callback):
        event = self.event(uid, method, name)
        return self.events.on(event, callback)
