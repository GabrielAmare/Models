from dataclasses import dataclass

from .base import Code

__all__ = ['Keywords', 'Symbols', 'CreateTable']


class Keywords:
    CREATE = "CREATE"
    TABLE = "TABLE"


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
