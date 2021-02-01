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

    @classmethod  # TO REMOVE
    def isUnknown(cls, user):
        return not user or user.is_anonymous

    @classmethod  # TO REMOVE
    def isSelf(cls, user, resource):
        return not cls.isUnknown(
            user) and resource and resource.__class__.__name__ == "User" and user.uid == resource.uid

    @classmethod  # TO REMOVE
    def isMember(cls, user):
        return not cls.isUnknown(user) and hasattr(user, 'role') and user.role == "MEMBER"

    @classmethod  # TO REMOVE
    def isAdmin(cls, user):
        return not cls.isUnknown(user) and hasattr(user, 'role') and user.role == "ADMIN"

    @classmethod
    def can(cls, user, action: str, resource: BaseModel = None):
        raise NotImplementedError

    on = can  # deprecated !

    @classmethod
    def can_read(cls, user, resource: BaseModel = None):
        return cls.can(user, cls.READ, resource)

    @classmethod
    def can_create(cls, user, resource: BaseModel = None):
        return cls.can(user, cls.CREATE, resource)

    @classmethod
    def can_update(cls, user, resource: BaseModel = None):
        return cls.can(user, cls.UPDATE, resource)

    @classmethod
    def can_soft_delete(cls, user, resource: BaseModel = None):
        return cls.can(user, cls.SOFT_DELETE, resource)

    @classmethod
    def can_hard_delete(cls, user, resource: BaseModel = None):
        return cls.can(user, cls.HARD_DELETE, resource)

    @classmethod
    def can_restore(cls, user, resource: BaseModel = None):
        return cls.can(user, cls.RESTORE, resource)
