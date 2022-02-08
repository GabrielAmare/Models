"""
    Useful references :
        - https://www.sqlite.org/syntaxdiagrams.html
"""
from __future__ import annotations

from abc import ABC
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Union

from .base import Code

__all__ = [
    'Keywords',
    'Symbols',
    'CreateTable',
    'ColumnConstraint',
    'PrimaryKey',
    'NotNull',
    'Unique',
    'Check',
    'Default',
    'Collate',
    'Action',
    'ForeignKeyClause',
    'Generated',
    'ColumnDefinition'
]


class Keywords:
    CREATE = "CREATE"
    TABLE = "TABLE"
    CONSTRAINT = "CONSTRAINT"
    PRIMARY = "PRIMARY"
    KEY = "KEY"
    AUTOINCREMENT = "AUTOINCREMENT"
    NOT = "NOT"
    NULL = "NULL"
    UNIQUE = "UNIQUE"
    CHECK = "CHECK"
    DEFAULT = "DEFAULT"
    COLLATE = "COLLATE"
    GENERATED = "GENERATED"
    ALWAYS = "ALWAYS"
    AS = "AS"
    STORED = "STORED"
    VIRTUAL = "VIRTUAL"
    REFERENCES = "REFERENCES"
    SET = "SET"
    CASCADE = "CASCADE"
    RESTRICT = "RESTRICT"
    NO = "NO"
    ACTION = "ACTION"
    ON = "ON"
    DELETE = "DELETE"
    UPDATE = "UPDATE"
    MATCH = "MATCH"
    TEMPORARY = "TEMPORARY"
    IF = "IF"
    EXISTS = "EXISTS"


class Symbols:
    SPACE = " "
    NEWLINE = "\n"
    SEMICOLON = ";"
    COMMA = ","
    LP = "("
    RP = ")"
    DOT = "."


@dataclass
class CreateTable(Code):
    name: str
    columns: list[ColumnDefinition] = field(default_factory=list)
    if_not_exists: bool = False
    temporary: bool = False
    schema_name: Optional[str] = None
    select_stmt: Optional[SelectStatement] = None

    def tokens(self) -> list[str]:
        tokens = [
            Keywords.CREATE,
            Symbols.SPACE
        ]

        if self.temporary:
            tokens.extend([
                Keywords.TEMPORARY,
                Symbols.SPACE
            ])

        tokens.extend([
            Keywords.TABLE,
            Symbols.SPACE
        ])

        if self.if_not_exists:
            tokens.extend([
                Keywords.IF,
                Symbols.SPACE,
                Keywords.NOT,
                Symbols.SPACE,
                Keywords.EXISTS,
                Symbols.SPACE
            ])

        if self.schema_name:
            tokens.extend([
                self.schema_name,
                Symbols.DOT
            ])

        tokens.extend([
            self.name,
            Symbols.SPACE
        ])

        if self.select_stmt:
            tokens.extend([
                Keywords.AS,
                Symbols.SPACE,
                *self.select_stmt.tokens()
            ])
        
        else:
            tokens.append(Symbols.LP)

            for index, column_def in enumerate(self.columns):
                if index:
                    tokens.extend([
                        Symbols.COMMA,
                        Symbols.SPACE
                    ])

                tokens.extend(column_def.tokens())

            # TODO : add 'table-constraint' part.

            tokens.append(Symbols.RP)

            # TODO : add 'table-option' part.

        tokens.append(Symbols.SEMICOLON)

        return tokens


class ColumnConstraint(Code, ABC):
    ...


class Order(str, Enum):
    ASC = "ASC"
    DESC = "DESC"


@dataclass
class PrimaryKey(ColumnConstraint):
    conflict_clause: ConflictClause
    auto_increment: bool = False
    name: Optional[str] = None
    order: Optional[Order] = None

    def tokens(self) -> list[str]:
        tokens = []

        if self.name:
            tokens.extend([
                Keywords.CONSTRAINT,
                Symbols.SPACE,
                self.name,
                Symbols.SPACE
            ])

        tokens.extend([
            Keywords.PRIMARY,
            Symbols.SPACE,
            Keywords.KEY,
            Symbols.SPACE
        ])

        if self.order:
            tokens.extend([
                self.order.name,
                Symbols.SPACE
            ])

        tokens.extend(self.conflict_clause.tokens())

        if self.auto_increment:
            tokens.extend([
                Symbols.SPACE,
                Keywords.AUTOINCREMENT
            ])

        return tokens


@dataclass
class NotNull(ColumnConstraint):
    conflict_clause: ConflictClause
    name: Optional[str] = None

    def tokens(self) -> list[str]:
        tokens = []

        if self.name:
            tokens.extend([
                Keywords.CONSTRAINT,
                Symbols.SPACE,
                self.name,
                Symbols.SPACE
            ])

        tokens.extend([
            Keywords.NOT,
            Symbols.SPACE,
            Keywords.NULL,
            Symbols.SPACE
        ])

        tokens.extend(self.conflict_clause.tokens())

        return tokens


@dataclass
class Unique(ColumnConstraint):
    conflict_clause: ConflictClause
    name: Optional[str] = None

    def tokens(self) -> list[str]:
        tokens = []

        if self.name:
            tokens.extend([
                Keywords.CONSTRAINT,
                Symbols.SPACE,
                self.name,
                Symbols.SPACE
            ])

        tokens.extend([
            Keywords.UNIQUE,
            Symbols.SPACE
        ])

        tokens.extend(self.conflict_clause.tokens())

        return tokens


@dataclass
class Check(ColumnConstraint):
    expr: Expression
    name: Optional[str] = None

    def tokens(self) -> list[str]:
        tokens = []

        if self.name:
            tokens.extend([
                Keywords.CONSTRAINT,
                Symbols.SPACE,
                self.name,
                Symbols.SPACE
            ])

        tokens.extend([
            Keywords.CHECK,
            Symbols.LP,
            *self.expr.tokens(),
            Symbols.RP
        ])

        return tokens


@dataclass
class Default(ColumnConstraint):
    expr: Union[Expression, LiteralValue, SignedNumber]
    name: Optional[str] = None

    def tokens(self) -> list[str]:
        tokens = []

        if self.name:
            tokens.extend([
                Keywords.CONSTRAINT,
                Symbols.SPACE,
                self.name,
                Symbols.SPACE
            ])

        tokens.extend([
            Keywords.DEFAULT,
        ])

        if isinstance(self.expr, Expression):
            tokens.extend([
                Symbols.LP,
                *self.expr.tokens(),
                Symbols.RP
            ])
        elif isinstance(self.expr, (LiteralValue, SignedNumber)):
            tokens.extend([
                Symbols.SPACE,
                *self.expr.tokens()
            ])
        else:
            raise Exception

        return tokens


@dataclass
class Collate(ColumnConstraint):
    collation_name: CollationName
    name: Optional[str] = None

    def tokens(self) -> list[str]:
        tokens = []

        if self.name:
            tokens.extend([
                Keywords.CONSTRAINT,
                Symbols.SPACE,
                self.name,
                Symbols.SPACE
            ])

        tokens.extend([
            Keywords.COLLATE,
            *self.collation_name.tokens()
        ])

        return tokens


class _Action(Code, ABC):
    ...


class _SetNull(_Action):
    def tokens(self) -> list[str]:
        return [
            Keywords.SET,
            Symbols.SPACE,
            Keywords.NULL
        ]


class _SetDefault(_Action):
    def tokens(self) -> list[str]:
        return [
            Keywords.SET,
            Symbols.SPACE,
            Keywords.DEFAULT
        ]


class _Cascade(_Action):
    def tokens(self) -> list[str]:
        return [
            Keywords.CASCADE
        ]


class _Restrict(_Action):
    def tokens(self) -> list[str]:
        return [
            Keywords.RESTRICT
        ]


class _NoAction(_Action):
    def tokens(self) -> list[str]:
        return [
            Keywords.NO,
            Symbols.SPACE,
            Keywords.ACTION
        ]


class Action:
    SET_NULL = _SetNull()
    SET_DEFAULT = _SetDefault()
    CASCADE = _Cascade()
    RESTRICT = _Restrict()
    NO_ACTION = _NoAction()


@dataclass
class ForeignKeyClause(ColumnConstraint):
    foreign_table: str
    column_names: list[str] = field(default_factory=list)
    on_delete: Optional[_Action] = None
    on_update: Optional[_Action] = None
    match_name: Optional[str] = None
    name: Optional[str] = None

    def tokens(self) -> list[str]:
        tokens = [
            Keywords.REFERENCES,
            Symbols.SPACE,
            self.foreign_table,
            Symbols.SPACE,
        ]

        if self.column_names:
            tokens.append(Symbols.LP)

            for index, column_name in enumerate(self.column_names):
                if index:
                    tokens.extend([
                        Symbols.COMMA,
                        Symbols.SPACE
                    ])

                tokens.append(column_name)

            tokens.append(Symbols.RP)

        if self.on_delete:
            tokens.extend([
                Symbols.SPACE,
                Keywords.ON,
                Symbols.SPACE,
                Keywords.DELETE,
                Symbols.SPACE,
                *self.on_delete.tokens()
            ])

        if self.on_update:
            tokens.extend([
                Symbols.SPACE,
                Keywords.ON,
                Symbols.SPACE,
                Keywords.UPDATE,
                Symbols.SPACE,
                *self.on_update.tokens()
            ])

        if self.match_name:
            tokens.extend([
                Symbols.SPACE,
                Keywords.MATCH,
                Symbols.SPACE,
                self.match_name
            ])

        # TODO : include 'DEFERRABLE' part.

        return tokens


@dataclass
class Generated(ColumnConstraint):
    expr: Expression
    always: bool = False
    stored: bool = False
    virtual: bool = False
    name: Optional[str] = None

    def __post_init__(self):
        assert not (self.stored and self.virtual), "A field can't be STORED and VIRTUAL"

    def tokens(self) -> list[str]:
        tokens = []

        if self.always:
            tokens.extend([
                Keywords.GENERATED,
                Symbols.SPACE,
                Keywords.ALWAYS,
                Symbols.SPACE
            ])

        tokens.extend([
            Keywords.AS,
            Symbols.LP,
            *self.expr.tokens(),
            Symbols.RP
        ])

        if self.stored:
            tokens.extend([
                Symbols.SPACE,
                Keywords.STORED
            ])

        elif self.virtual:
            tokens.extend([
                Symbols.SPACE,
                Keywords.VIRTUAL
            ])

        return tokens


@dataclass
class TypeName(Code):
    name: str
    args: list[str] = field(default_factory=list)

    def tokens(self) -> list[str]:
        tokens = [
            self.name
        ]

        if self.args:
            tokens.append(Symbols.LP)

            for index, arg in enumerate(self.args):
                if index:
                    tokens.extend([
                        Symbols.COMMA,
                        Symbols.SPACE
                    ])
                tokens.append(arg)

            tokens.append(Symbols.RP)

        return tokens


@dataclass
class ColumnDefinition(Code):
    name: str
    datatype: Optional[TypeName] = None
    constraints: list[ColumnConstraint] = field(default_factory=list)

    def tokens(self) -> list[str]:
        tokens = [
            self.name
        ]

        if self.datatype:
            tokens.extend([
                Symbols.SPACE,
                *self.datatype.tokens()
            ])

        if self.constraints:
            for constraint in self.constraints:
                tokens.append(Symbols.SPACE)
                tokens.extend(constraint.tokens())

        return tokens
