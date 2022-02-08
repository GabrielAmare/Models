from dataclasses import dataclass

from models import datatypes as dt

__all__ = [
    'Field',
    'Model'
]


@dataclass
class Field:
    name: str
    datatype: dt.DataType


@dataclass
class Model:
    name: str
    fields: list[Field]
