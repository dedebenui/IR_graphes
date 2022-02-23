from dataclasses import dataclass, fields
import datetime
from enum import Enum
from typing import Any, Iterator, Optional, Union
from dataclasses import field
import numpy as np

from emsapp.config import Config
from emsapp.data.validators import district_validator


class DataType(Enum):
    LINE="line"
    BAR="bar"
    PERIOD="period"


@dataclass
class RawData:
    headers: list[str]
    rows: list[list]


@dataclass
class DataReport:
    """
    data hangs to one of these as it is being transformed so that we
    can trace its path throught the process
    """
    filter:dict[str, str] = field(default_factory=dict)
    splitter:dict[str, str] = field(default_factory=dict)
    transformer:dict[str, str] = field(default_factory=dict)
    grouper:dict[str, str] = field(default_factory=dict)

@dataclass
class Entry:
    date_start: datetime.datetime
    date_end: datetime.datetime
    role: str
    institution: str
    institution_type: str
    location: str

    def __post_init__(self):
        if not isinstance(self.date_start, datetime.datetime):
            self.date_start = parse_date(self.date_start)

        if not isinstance(self.date_end, datetime.datetime):
            self.date_end = parse_date(self.date_end)

    @classmethod
    def fields(cls) -> list[str]:
        return [f.name for f in fields(cls)]

    @property
    def district(self) -> Optional[str]:
        """district corresponding to the location. May be None if data is unavailable"""
        return Config().user_data.get(N_("district"), self.location, district_validator)


class Entries:
    l: list[Entry]
    report: DataReport

    def __init__(self, l: list[Entry], report=None):
        self.l = l
        self.report = report or DataReport()

    def __iter__(self) -> Iterator[Entry]:
        yield from self.l

    def __getitem__(self, index: int) -> Entry:
        return self.l[index]

@dataclass
class FinalData:
    x:np.ndarray
    y:np.ndarray
    data_type:DataType
    report:DataReport


@dataclass
class DataSet:
    title:str
    data:list[FinalData]

    def __iter__(self)->Iterator[FinalData]:
        yield from self.data




def parse_date(s: Union[int, str, datetime.datetime, datetime.date]) -> datetime.datetime:
    """Returns a datetime object, parsed from a variety of different sources

    Parameters
    ----------
    s : Union[int, str, datetime.datetime, datetime.date, datetime.time]
        input

    Returns
    -------
    datetime.datetime
        parsed datetime
    """

    if not isinstance(s, (int, str, datetime.datetime, datetime.date)):
        raise ValueError(_("{0!r} cannot be interpreted as a date").format(s))

    if isinstance(s, datetime.datetime):
        return s
    if isinstance(s, datetime.date):
        return datetime.datetime.combine(s, datetime.time(0))
    if isinstance(s, int):
        if s > 40177 and s < 47482:
            return datetime.datetime(Config().data.excel_start_date, 1, 1) + datetime.timedelta(
                s - 1
            )

    s = s.strip()

    try:
        return datetime.datetime.fromisoformat(s)
    except ValueError:
        pass

    for fmt in Config().data.date_formats:
        try:
            return datetime.datetime.strptime(s, fmt)
        except ValueError:
            pass
    raise ValueError(_("{0!r} cannot be interpreted as a date").format(s))
