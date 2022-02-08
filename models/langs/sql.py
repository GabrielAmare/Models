"""
    Useful references :
        - https://www.sqlite.org/syntaxdiagrams.html
"""
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


class Symbols:
    SPACE = " "
    NEWLINE = "\n"
    SEMICOLON = ";"
    COMMA = ","
    LP = "("
    RP = ")"


@dataclass
class CreateTable(Code):
    name: str

    def tokens(self) -> list[str]:
        return [
            Keywords.CREATE,
            Symbols.SPACE,
            Keywords.TABLE,
            Symbols.SPACE,
            self.name,
            Symbols.SPACE,
            Symbols.LP,
            # TODO : add fields
            Symbols.RP,
            Symbols.SEMICOLON
        ]


class ColumnConstraint(Code):
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


@dataclass
class ColumnDefinition(Code):
    name: str
    datatype: Optional[str] = None
    constraints: list[ColumnConstraint] = field(default_factory=list)

    def tokens(self) -> list[str]:
        tokens = [
            self.name
        ]

        if self.datatype:
            tokens.append(Symbols.SPACE)
            tokens.append(self.datatype)

        if self.constraints:
            for constraint in self.constraints:
                tokens.append(Symbols.SPACE)
                tokens.extend(constraint.tokens())

        return tokens
