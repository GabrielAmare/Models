from dataclasses import dataclass

from .abc import DataType

__all__ = [
    'TimeDataType',
    'DATE',
    'DATETIME',
    'TIMESTAMP',
    'TIME',
    'YEAR'
]


class TimeDataType(DataType):
    """Date and Time Data Types"""


@dataclass
class _DATE(TimeDataType):
    """
        DATE
            A date.
            Format: YYYY-MM-DD.
            The supported range is from '1000-01-01' to '9999-12-31'
    """


DATE = _DATE()


@dataclass
class DATETIME(TimeDataType):
    """
        DATETIME(fsp)
        A date and time combination.
        Format: YYYY-MM-DD hh:mm:ss.
        The supported range is from '1000-01-01 00:00:00' to '9999-12-31 23:59:59'.
        Adding DEFAULT and ON UPDATE in the column definition to get
            automatic initialization and updating to the current date and time
    """
    fsp: int


@dataclass
class TIMESTAMP(TimeDataType):
    """
        TIMESTAMP(fsp)
            A timestamp.
            TIMESTAMP values are stored as the number of seconds since the Unix epoch ('1970-01-01 00:00:00' UTC).
            Format: YYYY-MM-DD hh:mm:ss.
            The supported range is from '1970-01-01 00:00:01' UTC to '2038-01-09 03:14:07' UTC.
            Automatic initialization and updating to the current date and time can be specified using
                DEFAULT CURRENT_TIMESTAMP and ON UPDATE CURRENT_TIMESTAMP in the column definition
    """
    fsp: int


@dataclass
class TIME(TimeDataType):
    """
        TIME(fsp)
            A time.
            Format: hh:mm:ss.
            The supported range is from '-838:59:59' to '838:59:59'
    """
    fsp: int


@dataclass
class _YEAR(TimeDataType):
    """
        YEAR
            A year in four-digit format. Values allowed in four-digit format: 1901 to 2155, and 0000.
            MySQL 8.0 does not support year in two-digit format.
    """


YEAR = _YEAR()
