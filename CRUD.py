import re
from models.utils import Attribute, Query
from .BaseModel import BaseModel, DeleteMode, RequestMode
from .BaseRights import BaseRights

regex_int = re.compile(r'^-?[0-9]+$')


def accord(name):
    return 'an ' if name.lower()[0] in 'aeiouy' else 'a ' + name


class RightsError(Exception):
    pass


class CRUD:
    """Handle operations on the models using a current auth and a rights management system"""

    crud_list = Query()

    @staticmethod
    def get(model):
        return CRUD.crud_list.copy().where(model=model).first

    @staticmethod
    def add(crud):
        CRUD.crud_list.append(crud)

    def __init__(self, model):
        self.model = model

        self.add(self)

    @property
    def rights(self):
        return self.model.__rights__

    @classmethod
    def value_right(cls, rights, name, value) -> bool:
        if isinstance(rights, dict) and name in rights:
            right = rights.get(name)
        else:
            return rights is True

        if hasattr(right, '__iter__'):
            return value in right
        elif hasattr(right, '__call__'):
            return right(value)
        else:
            return right is True

    @staticmethod
    def parse_uid(uid) -> int:
        if uid is None:
            return 0
        elif isinstance(uid, int):
            return uid
        elif isinstance(uid, str) and regex_int.match(uid):
            return int(uid)
        else:
            raise Exception(f"Incorrect uid : {repr(uid)} [{type(uid).__name__}]")

    ####################################################################################################################
    # CRUD SERVER
    ####################################################################################################################

    def apply_server(self, user, uid: int, data: dict):
        uid = CRUD.parse_uid(uid)
        if uid == 0:
            return self.create_server(user=user, data=data)
        elif uid > 0:
            if data:
                return self.update_server(user=user, uid=uid, data=data)
            else:
                return self.read_server(user=user, uid=uid)
        elif uid < 0:
            return self.delete_server(user=user, uid=-uid)
        else:
            raise Exception(f"Invalid integer ! {uid}")

    def create_server(self, user, data: dict) -> BaseModel:
        rights = self.rights and self.rights.on(user=user, action="create", resource=None)

        print(rights)

        if rights in (None, False):
            raise RightsError(f"You can't create {accord(self.model.__name__)}")

        return self.apply_resource(user=user, uid=0, data=data, rights=rights)

    def read_server(self, user, uid: int) -> BaseModel:
        resource = self.model.__get_instance__(uid)

        rights = self.rights and self.rights.on(user=user, action="read", resource=resource)

        if rights in (None, False):
            raise RightsError(f"You can't update {self.model.__name__}:{uid}")

        return resource

    def update_server(self, user, uid: int, data: dict) -> BaseModel:
        rights = self.rights and self.rights.on(user=user, action="update", resource=self.model.__get_instance__(uid))

        if rights in (None, False):
            raise RightsError(f"You can't update {self.model.__name__}:{uid}")

        return self.apply_resource(user=user, uid=uid, data=data, rights=rights)

    def delete_server(self, user, uid: int, mode=None):
        mode = {DeleteMode.SOFT: "soft", DeleteMode.HARD: "hard"}[self.model.__on_delete__(mode)]

        resource = self.model.__get_instance__(uid)

        rights = self.rights and self.rights.on(user=user, action=mode + "_delete", resource=resource)

        if rights in (None, False):
            raise RightsError(f"You can't {mode} delete {self.model.__name__}:{uid}")

        resource.delete(soft={"soft": True, "hard": False}[mode])

    ####################################################################################################################
    # CRUD CLIENT
    ####################################################################################################################

    def apply_client(self, user, uid: int, data: dict, format: dict, mode):
        uid = CRUD.parse_uid(uid)
        if uid == 0:
            return self.create_client(user=user, data=data, format=format, mode=mode)
        elif uid > 0:
            if data:
                return self.update_client(user=user, uid=uid, data=data, format=format, mode=mode)
            else:
                return self.read_client(user=user, uid=uid, format=format, mode=mode)
        elif uid < 0:
            return self.delete_client(user=user, uid=-uid)
        else:
            raise Exception(f"Invalid integer ! {uid}")

    def create_client(self, user, data: dict, format: dict, mode=RequestMode.LAZY) -> dict:
        if self.model.debug:
            print(f"CREATE : {self.model.__name__}")
        resource = self.apply_server(user=user, uid=0, data=data)
        client_data = self.read_client(user=user, uid=resource.uid, format=format, mode=mode)
        return client_data

    def read_client(self, user, uid: int, format: dict, mode=RequestMode.LAZY) -> dict:
        if self.model.debug:
            print(f"READ : {self.model.__name__}:{uid}")
        assert uid > 0
        resource = self.apply_server(user=user, uid=uid, data={})

        rights = self.rights and self.rights.on(user=user, action="read", resource=resource)

        client_data = self.read_resource(user=user, resource=resource, format=format, rights=rights, mode=mode)
        return client_data

    def update_client(self, user, uid: int, data: dict, format: dict, mode=RequestMode.LAZY) -> dict:
        if self.model.debug:
            print(f"UPDATE : {self.model.__name__}:{uid}")
        assert uid > 0
        resource = self.apply_server(user=user, uid=uid, data=data)
        client_data = self.read_client(user=user, uid=resource.uid, format=format, mode=mode)
        return client_data

    def delete_client(self, user, uid: int) -> dict:
        if self.model.debug:
            print(f"DELETE : {self.model.__name__}:{uid}")
        assert uid > 0
        self.apply_server(user=user, uid=-uid, data={})
        client_data = {}
        return client_data

    ####################################################################################################################
    # RESTORE
    ####################################################################################################################

    def restore(self, user, uid: int) -> None:
        if self.rights and self.rights.cant(user, BaseRights.RESTORE, self.model):
            raise RightsError(f"You can't restore {self.model.__name__}:{uid}")
        else:
            self.model.restore(uid)

    ####################################################################################################################
    # APPLY
    ####################################################################################################################

    @staticmethod
    def apply_value(user, model, client_value) -> BaseModel:
        """

        :param user: The current authenticated auth
        :param model: The model for the value to be created
        :param client_value: The value to be created
        :return:
        """
        if value_crud := CRUD.get(model):
            if isinstance(client_value, model):
                return client_value
            elif isinstance(client_value, int):
                return value_crud.apply_server(user=user, uid=client_value, data={})
            elif isinstance(client_value, dict):
                uid = client_value.pop('uid', 0)
                return value_crud.apply_server(user=user, uid=uid, data=client_value)
            else:
                return client_value
        else:
            return client_value

    @classmethod
    def apply_attribute(cls, user, attribute, client_value):
        if not attribute.model:
            return client_value
        elif client_value is not None:
            if isinstance(client_value, (tuple, list, Query)):
                server_value = []
                for client_item in client_value:
                    try:
                        server_item = cls.apply_value(user=user, model=attribute.model, client_value=client_item)
                    except RightsError:
                        continue
                    if server_item is not None:
                        server_value.append(server_item)
                return server_value
            else:
                return cls.apply_value(user=user, model=attribute.model, client_value=client_value)

    def apply_resource(self, user, uid: int, data: dict, rights) -> BaseModel:
        """

        :param user: The current authenticated auth
        :param uid: optional unique identifier (when specified, update method, else, create)
        :param data: The data to be created
        :return:
        """
        server_data = {}
        for name, client_value in data.items():
            if attribute := self.model.__get_attribute__(name):
                if self.value_right(rights=rights, name=name, value=client_value):
                    try:
                        server_value = self.apply_attribute(user, attribute, client_value)
                    except RightsError:
                        continue
                    server_data[attribute.name] = server_value

        if uid == 0:
            resource = self.model(**server_data).save()
        elif uid > 0:
            resource = self.model.__get_instance__(uid)
            if server_data:
                resource = resource.__update__(**server_data).save()
        else:
            resource = None

        return resource

    ####################################################################################################################
    # READ
    ####################################################################################################################

    @staticmethod
    def read_value(user, value, format):
        if format == ".uid":
            return value.uid
        elif isinstance(format, dict):
            if value_crud := value.__class__.__crud__:
                return value_crud.read_client(user=user, uid=value.uid, format=format, mode=RequestMode.LAZY)

    @classmethod
    def read_attribute(cls, user, resource: BaseModel, attribute: Attribute, format):
        value = attribute.get(resource)
        if format is None:
            return None
        elif not attribute.model:
            if isinstance(format, str):
                if format in ("str", "int", "bool", "float"):
                    return eval(format)(value)
            elif format is True:
                return value
            else:
                return None
        elif value is not None:
            if isinstance(value, (tuple, list, Query)):
                result = []
                for item in value:
                    try:
                        item = cls.read_value(user, item, format)
                    except RightsError:
                        continue
                    if item is not None:
                        result.append(item)
                return result
            else:
                return cls.read_value(user, value, format)

    def read_resource(self, user, resource: BaseModel, format: dict, rights, mode: str) -> dict:
        client_data = {}

        for attribute in self.model.__attributes__ \
                .where(private=False) \
                .keep(lambda a: mode == RequestMode.EAGER or not a.distant or a.on_lazy):
            try:
                value = self.read_attribute(user, resource, attribute, format.get(attribute.name))
            except RightsError:
                continue

            if self.value_right(rights=rights, name=attribute.name, value=value):
                if value is not None:
                    client_data[attribute.name] = value

        return client_data
