from datetime import datetime, date
from .utils import *
from .errors import *

from .Model import Model

from .API import API
from .CRUD import CRUD
from .BaseRights import BaseRights

from .Field import Field
from .ForeignKey import ForeignKey
from .Method import Method


def uid_increment(model):
    return max(model.__dbm__.max_uid, model.h.instances.getattr('uid').filter(None).max()) + 1


Field("uid", "int", unique=True, default=uid_increment, range=(0, float('inf')), static=True)(Model)
