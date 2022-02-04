from abc import abstractmethod, ABC
from functools import singledispatchmethod

from models.langs import javascript as js
from models.langs import python as py
from models.langs import sql
from .core import Model, Type

__all__ = [
    'Serializer',
    'PythonSerializer',
    'JavascriptSerializer',
    'SQLSerializer'
]


class Serializer(ABC):
    @abstractmethod
    def serialize(self, o) -> str:
        """"""


_PYTHON_TYPES = {
    Type.BOOLEAN: 'bool',
    Type.INTEGER: 'int',
    Type.DECIMAL: 'float',
    Type.STRING: 'str',
    Type.DATE: 'date',
    Type.DATETIME: 'datetime',
}


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
                            py.Typed(py.Var(field.name), py.Var(_PYTHON_TYPES[field.datatype]))
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
        code = sql.CreateTable(
            name=o.name
        )
        return str(code)
