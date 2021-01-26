import sys
import os
import shutil
import re

from .utils import FileMgmt


class DatabaseManagerError(Exception):
    def __init__(self, dbm, uid):
        self.dbm = dbm
        self.uid = uid


class DatabaseManagerCreateError(DatabaseManagerError):
    def __str__(self):
        return f"{repr(self.dbm.filepath(self.uid))} already exists in database, use 'update' instead of 'create'"


class DatabaseManagerReadError(DatabaseManagerError):
    def __str__(self):
        return f"{repr(self.dbm.filepath(self.uid))} does not exists in database, can't 'read' it"


class DatabaseManagerUpdateError(DatabaseManagerError):
    def __str__(self):
        return f"{repr(self.dbm.filepath(self.uid))} does not exists in database, use 'create' instead of 'update'"


class DatabaseManagerDeleteError(DatabaseManagerError):
    def __str__(self):
        return f"{repr(self.dbm.filepath(self.uid))} can't be deleted (already soft deleted version OR new version overwrite)"


class DatabaseManagerRestoreError(DatabaseManagerError):
    def __str__(self):
        return f"{repr(self.dbm.filepath(self.uid))} can't be restored (missing soft deleted version OR new version overwrite)"


class DatabaseManager:
    name_regex = re.compile(r'^-?[0-9]+$')

    def error(self, err_cls, uid):
        error = err_cls(self, uid)
        if self.model.__db_errs__:
            raise error
        elif self.model.__db_warns__:
            print(error, file=sys.stderr)

    def __init__(self, model, ext='.json'):
        assert hasattr(model, '__dbfp__'), \
            f"The DatabaseManager model must have a __dbfp__ (database filepath) attribute"
        assert hasattr(model, '__db_errs__'), \
            f"The DatabaseManager model must have a __db_errs__ attribute"
        assert hasattr(model, '__db_warns__'), \
            f"The DatabaseManager model must have a __db_warns__ attribute"
        self.model = model
        self.ext = ext
        self.max_uid = max([uid if uid > 0 else -uid for uid in self.listall(soft_deleted=True)], default=0)

    def mkdir(self):
        os.mkdir(self.filepath())

    def filepath(self, uid=None, soft_delete: bool = False):
        """ Return the base filepath or the filepath joined with the id"""
        if uid is None:
            return os.path.join(self.model.__dbfp__, self.model.__name__)
        else:
            assert isinstance(uid,
                              int) and uid > 0, f"DatabaseManager.filepath(uid={uid}) : uid is not a positive integer"
            if soft_delete:
                uid = -uid
            return os.path.join(self.model.__dbfp__, self.model.__name__, f"{uid}{self.ext}")

    def exists(self, uid: int = None, soft_delete: bool = False) -> bool:
        """Return True if the instance already exists in database"""
        fp = self.filepath(uid, soft_delete=soft_delete)
        return os.path.exists(fp)

    def create(self, data: dict) -> None:
        uid = data.pop('uid')
        self.max_uid = max(self.max_uid, uid)

        if self.exists(uid):
            return self.error(DatabaseManagerCreateError, uid)

        dbfp = self.filepath(uid, soft_delete=False)
        FileMgmt.save_json(fp=dbfp, data=data)
        print(f"DatabaseManager: {self.model.__name__}:{uid} created !")

    def read(self, uid: int) -> dict:
        if not self.exists(uid):
            self.error(DatabaseManagerReadError, uid)
            return {uid: uid}

        dbfp = self.filepath(uid, soft_delete=False)
        data = FileMgmt.load_json(fp=dbfp)
        data['uid'] = uid
        return data

    def update(self, data: dict) -> None:
        uid = data.pop('uid')

        if not self.exists(uid):
            return self.error(DatabaseManagerUpdateError, uid)

        dbfp = self.filepath(uid, soft_delete=False)
        FileMgmt.save_json(fp=dbfp, data=data)
        print(f"DatabaseManager: {self.model.__name__}:{uid} updated !")

    def delete(self, uid: int, soft: bool = False) -> None:
        if not self.exists(uid, soft_delete=False):
            return self.error(DatabaseManagerDeleteError, uid)
        if soft and self.exists(uid, soft_delete=True):
            return self.error(DatabaseManagerDeleteError, uid)

        dbfp = self.filepath(uid, soft_delete=False)
        if soft:
            sdfp = self.filepath(uid, soft_delete=True)
            shutil.copyfile(dbfp, sdfp)

        os.remove(dbfp)
        print(f"DatabaseManager: {self.model.__name__}:{uid} {'soft' if soft else 'hard'} deleted !")

    def restore(self, uid: int) -> None:
        if self.exists(uid, soft_delete=False):
            return self.error(DatabaseManagerRestoreError, uid)
        if not self.exists(uid, soft_delete=True):
            return self.error(DatabaseManagerRestoreError, uid)

        dbfp = self.filepath(uid, soft_delete=False)
        sdfp = self.filepath(uid, soft_delete=True)
        shutil.copyfile(sdfp, dbfp)
        os.remove(sdfp)

        print(f"DatabaseManager: {self.model.__name__}:{uid} restored !")

    def save(self, data: dict):
        uid = data.get('uid')
        if self.exists(uid):
            self.update(data)
        else:
            self.create(data)

    def listall(self, soft_deleted=False):
        if os.path.exists(self.filepath()):
            for dbfp in os.listdir(self.filepath()):
                name, ext = os.path.splitext(dbfp)
                if ext == self.ext:
                    if self.name_regex.match(name):
                        uid = int(name)
                        if soft_deleted or uid > 0:
                            yield uid
