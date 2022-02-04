from abc import abstractmethod, ABC
from functools import singledispatchmethod

from models.langs import javascript as js
from models.langs import python as py
from models.langs import sql
from models.langs.base import Code
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


class Server:
    @classmethod
    def model_dataclass(cls, model: Model) -> Code:
        return py.Module([
            py.ImportFrom(py.Var("dataclasses"), py.Var("dataclass")),

            py.Decorator(
                base=py.Var('dataclass'),
                over=py.Class(
                    name=model.name,
                    block=py.Block(
                        [
                            py.Typed(py.Var(field.name), py.Var(_PYTHON_TYPES[field.datatype]))
                            for field in model.fields
                        ] if model.fields else py.PASS
                    )
                )
            )
        ])

    @classmethod
    def model_class(cls, model: Model) -> Code:
        __init__method = py.Def(
            name='__init__',
            args=py.Args([
                py.SELF,
                *[
                    py.Typed(py.Var(field.name), py.Var(_PYTHON_TYPES[field.datatype]))
                    for field in model.fields
                ]
            ]),
            block=py.Block([
                py.Assign(py.Getattr(py.SELF, py.Var(field.name)), py.Var(field.name))
                for field in model.fields
            ])
        )

        return py.Class(
            name=model.name,
            block=py.Block([
                __init__method
            ])
        )


class PythonSerializer(Serializer):
    @singledispatchmethod
    def serialize(self, o) -> str:
        raise NotImplementedError

    @serialize.register
    def _(self, o: Model) -> str:
        return str(Server.model_dataclass(o))


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
