from dataclasses import dataclass

from .abc import DataType

__all__ = [
    'StringDataType',
    'CHAR',
    'VARCHAR',
    'BINARY',
    'VARBINARY',
    'BLOB',
    'TINYBLOB',
    'MEDIUMBLOB',
    'LONGBLOB',
    'TEXT',
    'TINYTEXT',
    'MEDIUMTEXT',
    'LONGTEXT',
    'ENUM',
    'SET'
]


class StringDataType(DataType):
    """String Data Types"""


########################################################################################################################
# CHAR & BINARY
########################################################################################################################


@dataclass
class CHAR(StringDataType):
    """
        CHAR(size)
            A FIXED length string (can contain letters, numbers, and special characters).
            The size parameter specifies the column length in characters - can be from 0 to 255.
            Default is 1
    """
    size: int = 1

    def __post_init__(self):
        assert 0 <= self.size < 256


@dataclass
class VARCHAR(StringDataType):
    """
        VARCHAR(size)
            A VARIABLE length string (can contain letters, numbers, and special characters).
            The size parameter specifies the maximum column length in characters - can be from 0 to 65535
    """
    size: int

    def __post_init__(self):
        assert 0 <= self.size < 65536


@dataclass
class BINARY(StringDataType):
    """
        BINARY(size)
        Equal to CHAR(), but stores binary byte strings.
        The size parameter specifies the column length in bytes.
        Default is 1
    """
    size: int = 1

    def __post_init__(self):
        assert 0 <= self.size < 256


@dataclass
class VARBINARY(StringDataType):
    """
        VARBINARY(size)
            Equal to VARCHAR(), but stores binary byte strings.
            The size parameter specifies the maximum column length in bytes.
    """
    size: int

    def __post_init__(self):
        assert 0 <= self.size < 65536


########################################################################################################################
# BLOBS
########################################################################################################################


@dataclass
class BLOB(StringDataType):
    """
        BLOB(size)
            For BLOBs (Binary Large Objects).
            Holds up to 65,535 bytes of data
    """
    size: int

    def __post_init__(self):
        assert 0 <= self.size < 65536


@dataclass
class _TINYBLOB(StringDataType):
    """
        TINYBLOB
            For BLOBs (Binary Large Objects).
            Max length: 255 bytes
    """


@dataclass
class _MEDIUMBLOB(StringDataType):
    """
        MEDIUMBLOB
            For BLOBs (Binary Large Objects).
            Holds up to 16,777,215 bytes of data
    """


@dataclass
class _LONGBLOB(StringDataType):
    """
        LONGBLOB
            For BLOBs (Binary Large Objects).
            Holds up to 4,294,967,295 bytes of data
    """


TINYBLOB = _TINYBLOB()
MEDIUMBLOB = _MEDIUMBLOB()
LONGBLOB = _LONGBLOB()


########################################################################################################################
# TEXTS
########################################################################################################################


@dataclass
class TEXT(StringDataType):
    """
        TEXT(size)
            Holds a string with a maximum length of 65,535 bytes
    """
    size: int

    def __post_init__(self):
        assert 0 <= self.size < 65536


@dataclass
class _TINYTEXT(StringDataType):
    """
        TINYTEXT
            Holds a string with a maximum length of 255 characters
    """


@dataclass
class _MEDIUMTEXT(StringDataType):
    """
        MEDIUMTEXT
            Holds a string with a maximum length of 16,777,215 characters
    """


@dataclass
class _LONGTEXT(StringDataType):
    """
        LONGTEXT
            Holds a string with a maximum length of 4,294,967,295 characters
    """


TINYTEXT = _TINYTEXT()
MEDIUMTEXT = _MEDIUMTEXT()
LONGTEXT = _LONGTEXT()


########################################################################################################################
# ENUM & SET
########################################################################################################################


@dataclass
class ENUM(StringDataType):
    """
        ENUM(val1, val2, val3, ...)
            A string object that can have only one value, chosen from a list of possible values.
            You can list up to 65535 values in an ENUM list.
            If a value is inserted that is not in the list, a blank value will be inserted.
            The values are sorted in the order you enter them
    """
    values: list[str]

    def __post_init__(self):
        assert len(self.values) <= 65535


@dataclass
class SET(StringDataType):
    """
        SET(val1, val2, val3, ...)
            A string object that can have 0 or more values, chosen from a list of possible values.
            You can list up to 64 values in a SET list
    """
    values: list[str]

    def __post_init__(self):
        assert len(self.values) <= 64
