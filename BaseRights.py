from flask_login import AnonymousUserMixin

from .BaseModel import BaseModel


class BaseRights:
    CREATE = "CREATE"
    READ = "READ"
    UPDATE = "UPDATE"
    SOFT_DELETE = "SOFT_DELETE"
    HARD_DELETE = "HARD_DELETE"
    RESTORE = "RESTORE"

    _unknown = False
    _create = False
    _read = False
    _update = False
    _soft_delete = False
    _hard_delete = False
    _restore = False

    @classmethod
    def isUnknown(cls, user):
        return not user or user.is_anonymous

    @classmethod
    def isSelf(cls, user, resource):
        return not cls.isUnknown(
            user) and resource and resource.__class__.__name__ == "User" and user.uid == resource.uid

    @classmethod
    def isMember(cls, user):
        return not cls.isUnknown(user) and hasattr(user, 'role') and user.role == "MEMBER"

    @classmethod
    def isAdmin(cls, user):
        return not cls.isUnknown(user) and hasattr(user, 'role') and user.role == "ADMIN"

    @classmethod
    def on(cls, user, action: str, resource: BaseModel = None):
        raise NotImplementedError
