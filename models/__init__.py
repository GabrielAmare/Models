from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from functools import singledispatchmethod

from models.langs import javascript as js
from models.langs import python as py


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


class Serializer(ABC):
    @abstractmethod
    def serialize(self, o) -> str:
        """"""


class PythonSerializer(Serializer):
    @singledispatchmethod
    def serialize(self, o) -> str:
        raise NotImplementedError

    @serialize.register
    def _(self, o: Model) -> str:
        code = py.Class(
            name=o.name,
            block=py.Block([
                py.Def(
                    name='__init__',
                    args=py.Args([
                        py.SELF,
                        *[
                            py.Var(field.name)
                            for field in o.fields
                        ]
                    ]),
                    block=py.Block([
                        py.Assign(py.Getattr(py.SELF, py.Var(field.name)), py.Var(field.name))
                        for field in o.fields
                    ])
                )
            ])
        )
        return str(code)


class JavascriptSerializer(Serializer):
    @singledispatchmethod
    def serialize(self, o) -> str:
        raise NotImplementedError

    @serialize.register
    def _(self, o: Model) -> str:
        code = js.Class(
            name=o.name,
            block=js.Block([
                js.Method(
                    name='constructor',
                    args=js.Args([
                        py.Var(field.name)
                        for field in o.fields
                    ]),
                    block=js.Block([
                        js.Assign(js.Getattr(js.THIS, js.Var(field.name)), js.Var(field.name))
                        for field in o.fields
                    ])
                )
            ])
        )
        return str(code)


class SQLSerializer(Serializer):
    @singledispatchmethod
    def serialize(self, o) -> str:
        raise NotImplementedError

    @serialize.register
    def _(self, o: Model) -> str:
        return f"CREATE TABLE {o.name} (" + ");"
