from dataclasses import dataclass
from enum import Enum

__all__ = [
    'Type',
    'Field',
    'Model'
]


class Type(str, Enum):
    BOOLEAN = "BOOLEAN"
    INTEGER = "INTEGER"
    DECIMAL = "DECIMAL"
    STRING = "STRING"
    DATE = "DATE"
    DATETIME = "DATETIME"


@dataclass
class Field:
    name: str
    datatype: Type


@dataclass
class Model:
    name: str
    fields: list[Field]
