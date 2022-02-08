from abc import abstractmethod, ABC
from functools import singledispatchmethod

from models import datatypes as dt
from models.langs import javascript as js
from models.langs import python as py
from models.langs import sql
from .core import Model

__all__ = [
    'Serializer',
    'PythonSerializer',
    'JavascriptSerializer',
    'SQLSerializer',
    'Server'
]


class Serializer(ABC):
    @abstractmethod
    def serialize(self, o) -> str:
        """"""


def _get_python_type(datatype) -> py.Var:
    if datatype is dt.BOOLEAN:
        return py.Var('bool')

    elif datatype is dt.DATE:
        return py.DATE

    elif datatype in (dt.TINYBLOB, dt.MEDIUMBLOB, dt.LONGBLOB):
        return py.Var('bytes')

    elif datatype in (dt.TINYTEXT, dt.MEDIUMTEXT, dt.LONGTEXT):
        return py.Var('str')

    elif isinstance(datatype, (dt.BIT, dt.TINYINT, dt.SMALLINT, dt.MEDIUMINT, dt.INTEGER, dt.BIGINT)):
        return py.Var('int')

    elif isinstance(datatype, (dt.FLOAT, dt.DOUBLE, dt.DECIMAL)):
        return py.Var('float')

    elif isinstance(datatype, dt.DATETIME):
        return py.DATETIME

    elif isinstance(datatype, (dt.BINARY, dt.VARBINARY, dt.BLOB)):
        return py.Var('bytes')

    elif isinstance(datatype, (dt.CHAR, dt.VARCHAR, dt.TEXT, dt.ENUM, dt.SET)):
        return py.Var('str')

    else:
        raise Exception(f"Mapping DataType -> py.Var not found for {datatype.__class__.__name__!r}!")


def _get_sql_type(datatype) -> sql.TypeName:
    if datatype is dt.BOOLEAN:
        return sql.TypeName('BOOLEAN')
    elif datatype is dt.DATE:
        return sql.TypeName('DATE')
    elif datatype is dt.TINYBLOB:
        return sql.TypeName('TINYBLOB')
    elif datatype is dt.MEDIUMBLOB:
        return sql.TypeName('MEDIUMBLOB')
    elif datatype is dt.LONGBLOB:
        return sql.TypeName('LONGBLOB')
    elif datatype is dt.TINYTEXT:
        return sql.TypeName('TINYTEXT')
    elif datatype is dt.MEDIUMTEXT:
        return sql.TypeName('MEDIUMTEXT')
    elif datatype is dt.LONGTEXT:
        return sql.TypeName('LONGTEXT')

    elif isinstance(datatype, (dt.BIT, dt.TINYINT, dt.SMALLINT, dt.MEDIUMINT, dt.INTEGER, dt.BIGINT)):
        return sql.TypeName(datatype.__class__.__name__, [str(datatype.size)])

    elif isinstance(datatype, (dt.FLOAT, dt.DOUBLE, dt.DECIMAL)):
        return sql.TypeName(datatype.__class__.__name__, [str(datatype.size)])

    elif isinstance(datatype, (dt.DATETIME, dt.TIME, dt.TIMESTAMP)):
        return sql.TypeName(datatype.__class__.__name__, [str(datatype.fsp)])

    elif isinstance(datatype, (dt.BINARY, dt.VARBINARY, dt.BLOB)):
        return sql.TypeName(datatype.__class__.__name__, [str(datatype.size)])

    elif isinstance(datatype, (dt.CHAR, dt.VARCHAR, dt.TEXT)):
        return sql.TypeName(datatype.__class__.__name__, [str(datatype.size)])

    elif isinstance(datatype, (dt.ENUM, dt.SET)):
        return sql.TypeName(datatype.__class__.__name__, list(map(str, datatype.values)))

    else:
        raise Exception(f"Mapping DataType -> sql.TypeName not found for {datatype.__class__.__name__!r}!")


class Server:
    @classmethod
    def model_dataclass(cls, model: Model) -> py.Module:
        imports: list[py.Statement] = [
            py.DATACLASS.import_info
        ]

        annotations: list[py.Statement] = []

        for field in model.fields:
            if isinstance(field.datatype, dt.DATETIME):
                imports.append(py.DATETIME.import_info)

            if field.datatype is dt.DATE:
                imports.append(py.DATE.import_info)

            annotations.append(
                py.Typed(py.Var(field.name), _get_python_type(field.datatype))
            )

        if not annotations:
            annotations.append(py.PASS)

        return py.Module([
            *imports,

            py.Decorator(
                base=py.DATACLASS,
                over=py.Class(
                    name=model.name,
                    block=py.Block(annotations)
                )
            )
        ])

    @classmethod
    def model_class(cls, model: Model) -> py.Module:
        imports: list[py.Statement] = []

        field_args = []
        field_attr = []

        for field in model.fields:
            if isinstance(field.datatype, dt.DATETIME):
                imports.append(py.DATETIME.import_info)

            if field.datatype is dt.DATE:
                imports.append(py.DATE.import_info)

            field_args.append(
                py.Typed(py.Var(field.name), _get_python_type(field.datatype))
            )
            field_attr.append(
                py.Assign(py.Getattr(py.SELF, py.Var(field.name)), py.Var(field.name))
            )

        __init__method = py.Def(
            name='__init__',
            args=py.Args([py.SELF, *field_args]),
            block=py.Block(field_attr)
        )

        return py.Module([
            *imports,
            py.Class(
                name=model.name,
                block=py.Block([
                    __init__method
                ])
            )
        ])

    @classmethod
    def model_classes(cls, models: list[Model]) -> py.Module:
        imports: list[py.Statement] = []
        classes: list[py.Class] = []

        for model in models:
            field_args = []
            field_attr = []

            for field in model.fields:
                if isinstance(field.datatype, dt.DATETIME):
                    imports.append(py.DATETIME.import_info)

                if field.datatype is dt.DATE:
                    imports.append(py.DATE.import_info)

                field_args.append(
                    py.Typed(py.Var(field.name), _get_python_type(field.datatype))
                )
                field_attr.append(
                    py.Assign(py.Getattr(py.SELF, py.Var(field.name)), py.Var(field.name))
                )

            __init__method = py.Def(
                name='__init__',
                args=py.Args([py.SELF, *field_args]),
                block=py.Block(field_attr)
            )
            model_class = py.Class(
                name=model.name,
                block=py.Block([
                    __init__method
                ])
            )
            classes.append(model_class)

        return py.Module([
            *imports,
            *classes
        ])


class PythonSerializer(Serializer):
    @singledispatchmethod
    def serialize(self, o) -> str:
        raise NotImplementedError

    @serialize.register
    def _(self, o: Model) -> str:
        return str(Server.model_class(o))


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
            name=o.name,
            if_not_exists=True,
            columns=[
                sql.ColumnDefinition(
                    name=field.name,
                    datatype=_get_sql_type(field.datatype)
                )
                for field in o.fields
            ],
            cfg_expand=True
        )
        return str(code)
