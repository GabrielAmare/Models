from abc import ABC
from dataclasses import dataclass
from typing import Union

from .base import Code

__all__ = [
    'Keywords',
    'Symbols',
    'Statement',
    'Block',
    'Class',
    'Def',
    'Var',
    'Str',
    'Args',
    'ImportFrom',
    'Module',
    'PASS',
    'CLS',
    'SELF'
]


class Keywords:
    CLASS = "class"
    PASS = "pass"
    DEF = "def"
    IMPORT = "import"
    FROM = "from"


class Symbols:
    NEWLINE = "\n"
    SPACE = " "
    INDENT = "    "
    COLON = ":"
    LP = "("
    RP = ")"
    COMMA = ","
    EQUAL = "="
    DOT = "."
    AT = "@"


class Statement(Code, ABC):
    ...


class Expression(Code, ABC):
    ...


class Object(Expression, ABC):
    ...


@dataclass
class Block(Code):
    statements: list[Statement]

    def tokens(self) -> list[str]:
        tokens = []

        for statement in self.statements:
            tokens.append(Symbols.NEWLINE)
            tokens.append(Symbols.INDENT)

            for token in statement.tokens():
                tokens.append(token)

                if token is Symbols.NEWLINE:
                    tokens.append(Symbols.INDENT)

        return tokens


@dataclass
class Class(Statement):
    name: str
    block: Block

    def tokens(self) -> list[str]:
        return [
            Keywords.CLASS,
            Symbols.SPACE,
            self.name,
            Symbols.COLON,
            *self.block.tokens()
        ]


@dataclass
class Var(Object):
    name: str

    def __post_init__(self):
        assert self.name.isidentifier()

    def tokens(self) -> list[str]:
        return [
            self.name
        ]


@dataclass
class Str(Object):
    value: str

    def tokens(self) -> list[str]:
        return [
            repr(self.value)
        ]


@dataclass
class Typed(Object):
    obj: Object
    typ: Var

    def tokens(self) -> list[str]:
        return [
            *self.obj.tokens(),
            Symbols.COLON,
            Symbols.SPACE,
            *self.typ.tokens()
        ]


@dataclass
class Args(Code):
    args: list[Var]

    def tokens(self) -> list[str]:
        tokens = []
        for index, arg in enumerate(self.args):
            if index:
                tokens.append(Symbols.COMMA)
                tokens.append(Symbols.SPACE)
            tokens.extend(arg.tokens())

        return tokens


@dataclass
class Def(Statement):
    name: str
    args: Args
    block: Block

    def tokens(self) -> list[str]:
        return [
            Keywords.DEF,
            Symbols.SPACE,
            self.name,
            Symbols.LP,
            *self.args.tokens(),
            Symbols.RP,
            Symbols.COLON,
            *self.block.tokens()
        ]


@dataclass
class Assign(Statement):
    obj: Object
    val: Expression

    def tokens(self) -> list[str]:
        return [
            *self.obj.tokens(),
            Symbols.SPACE,
            Symbols.EQUAL,
            Symbols.SPACE,
            *self.val.tokens()
        ]


@dataclass
class Getattr(Object):
    obj: Object
    key: Var

    def tokens(self) -> list[str]:
        return [
            *self.obj.tokens(),
            Symbols.DOT,
            *self.key.tokens()
        ]


class _Pass(Statement):
    def tokens(self) -> list[str]:
        return [Keywords.PASS]


@dataclass
class Decorator(Statement):
    base: Object
    over: Union['Decorator', Class, Def]

    def tokens(self) -> list[str]:
        return [
            Symbols.AT,
            *self.base.tokens(),
            Symbols.NEWLINE,
            *self.over.tokens()
        ]


@dataclass
class ImportFrom(Statement):
    import_: Object
    from_: Union[Var, Args]

    def tokens(self) -> list[str]:
        return [
            Keywords.FROM,
            Symbols.SPACE,
            *self.import_.tokens(),
            Symbols.SPACE,
            Keywords.IMPORT,
            Symbols.SPACE,
            *self.from_.tokens()
        ]


@dataclass
class Module(Code):
    statements: list[Statement]

    def tokens(self) -> list[str]:
        tokens = []
        imports = []
        statements = []

        for statement in self.statements:
            if isinstance(statement, ImportFrom):
                imports.append(statement)
            else:
                statements.append(statement)

        if imports:
            for statement in imports:
                tokens.extend(statement.tokens())
                tokens.append(Symbols.NEWLINE)

            tokens.append(Symbols.NEWLINE)
            tokens.append(Symbols.NEWLINE)

        for statement in statements:
            tokens.extend(statement.tokens())
            tokens.append(Symbols.NEWLINE)

        return tokens


PASS = _Pass()

CLS = Var('cls')
SELF = Var('self')
