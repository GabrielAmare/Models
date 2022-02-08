from dataclasses import dataclass

from .abc import DataType

__all__ = [
    'NumericDataType',
    'BIT',
    'BOOLEAN',
    'TINYINT',
    'SMALLINT',
    'MEDIUMINT',
    'INTEGER',
    'BIGINT',
    'FLOAT',
    'DOUBLE',
    'DECIMAL',
    'BOOL',
    'INT',
    'DEC'
]


class NumericDataType(DataType):
    """Numeric Data Types
        DEC(size, d) 	Equal to DECIMAL(size,d)
    """


@dataclass
class BIT(NumericDataType):
    """
        BIT(size)
            A bit-value type.
            The number of bits per value is specified in size.
            The size parameter can hold a value from 1 to 64.
            The default value for size is 1.

    """
    size: int = 1

    def __post_init__(self):
        assert 1 <= self.size <= 64


@dataclass
class _BOOLEAN(NumericDataType):
    """
        BOOL
            Zero is considered as false, nonzero values are considered as true.
        BOOLEAN
            Equal to BOOL

    """


BOOLEAN = _BOOLEAN()


@dataclass
class TINYINT(NumericDataType):
    """
        TINYINT(size)
            A very small integer.
            Signed range is from -128 to 127.
            Unsigned range is from 0 to 255.
            The size parameter specifies the maximum display width (which is 255)
    """
    size: int


@dataclass
class SMALLINT(NumericDataType):
    """
        SMALLINT(size)
            A small integer.
            Signed range is from -32768 to 32767.
            Unsigned range is from 0 to 65535.
            The size parameter specifies the maximum display width (which is 255)
    """
    size: int


@dataclass
class MEDIUMINT(NumericDataType):
    """
        MEDIUMINT(size)
            A medium integer.
            Signed range is from -8388608 to 8388607.
            Unsigned range is from 0 to 16777215.
            The size parameter specifies the maximum display width (which is 255)
    """
    size: int


@dataclass
class INTEGER(NumericDataType):
    """
        INTEGER(size)
            A medium integer.
            Signed range is from -2147483648 to 2147483647.
            Unsigned range is from 0 to 4294967295.
            The size parameter specifies the maximum display width (which is 255)

        INT(size)
            Equal to INT(size)
    """
    size: int


@dataclass
class BIGINT(NumericDataType):
    """
        BIGINT(size)
            A large integer.
            Signed range is from -9223372036854775808 to 9223372036854775807.
            Unsigned range is from 0 to 18446744073709551615.
            The size parameter specifies the maximum display width (which is 255)
    """
    size: int


@dataclass
class FLOAT(NumericDataType):
    """
        FLOAT(size, d)
            A floating point number.
            The total number of digits is specified in size.
            The number of digits after the decimal point is specified in the d parameter.
            This syntax is deprecated in MySQL 8.0.17, and it will be removed in future MySQL versions
    """
    size: int
    d: int


@dataclass
class FLOAT(NumericDataType):
    """
        FLOAT(p)
        A floating point number.
        MySQL uses the p value to determine whether to use FLOAT or DOUBLE for the resulting data type.
        If p is from 0 to 24, the data type becomes FLOAT().
        If p is from 25 to 53, the data type becomes DOUBLE()

    """
    size: int
    d: int


@dataclass
class DOUBLE(NumericDataType):
    """
        DOUBLE(size, d)
            A normal-size floating point number.
            The total number of digits is specified in size.
            The number of digits after the decimal point is specified in the d parameter
    """
    size: int
    d: int


@dataclass
class DECIMAL(NumericDataType):
    """
        DECIMAL(size, d)
            An exact fixed-point number.
            The total number of digits is specified in size.
            The number of digits after the decimal point is specified in the d parameter.
            The maximum number for size is 65.
            The maximum number for d is 30.
            The default value for size is 10.
            The default value for d is 0.
    """
    size: int = 10
    d: int = 0

    def __post_init__(self):
        assert 0 <= self.size <= 65
        assert 0 <= d <= 30


BOOL = BOOLEAN
INT = INTEGER
DEC = DECIMAL
