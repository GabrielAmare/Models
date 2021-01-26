from .utils import *

from .Model import Model

from .API import API
from .CRUD import CRUD
from .BaseRights import BaseRights

from .Field import Field
from .ForeignKey import ForeignKey
from .Method import Method

Field("uid", "int", unique=True, default=lambda model: model.__dbm__.max_uid + 1, range=(0, float('inf')))(Model)
