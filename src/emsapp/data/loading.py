from __future__ import annotations

from dataclasses import dataclass, fields
import datetime
import os
from pathlib import Path
from typing import Protocol, Type, Union

from emsapp.config import Config, ConfigurationValueError, DataConfig
from emsapp.data import RawData
from emsapp.logging import get_logger
from emsapp.i18n import _, ngettext

logger = get_logger()


class DataLoader(Protocol):
    def __init__(self, path: Path):
        """creates an importer from a path to a file

        Parameters
        ----------
        path : Path
            path the file containing the data
        """
        ...

    def load_data(self, config: DataConfig) -> tuple[list[str], list[list]]:
        """imports the whole dataset

        Parameters
        ----------
        config: DataConfig
            current data configuration


        Returns
        -------
        list[str]
            headers (column names)
        list[list]
            list of rows of data. Rows must have the same len as headers
        """
        ...

    def headers(self, config: DataConfig) -> list[str]:
        """Returns a list of the column names"""
        ...

    def tables(self, config: DataConfig) -> list[str]:
        """returns a list of available tables"""
        ...


class DataLoaderFactory:
    _registered: dict[str, Type[DataLoader]] = {}

    @classmethod
    def register(cls, specs: tuple[Union[str, tuple[str]], Type[DataLoader]]):
        ext, new_cls = specs
        if isinstance(ext, str):
            ext = (ext,)
        for e in ext:
            cls._registered[e] = new_cls

    @classmethod
    def create(cls, path: os.PathLike) -> DataLoader:
        path = Path(path)
        ext = path.suffix.lower()
        return cls._registered[ext](path)

    @classmethod
    def all_extensions(cls) -> list[str]:
        return list(cls._registered)

    @classmethod
    def valid(cls, path: Path) -> bool:
        return path.suffix.lower() in cls._registered


@dataclass
class Entry:
    date_start: datetime.datetime
    date_end: datetime.datetime
    role: str
    institution: str
    location: str

    def __post_init__(self):
        if not isinstance(self.date_start, datetime.datetime):
            self.date_start = parse_date(self.date_start)

        if not isinstance(self.date_end, datetime.datetime):
            self.date_end = parse_date(self.date_end)

    @classmethod
    def fields(cls) -> list[str]:
        return sorted(fields(cls))

    @property
    def district(self) -> str:
        return Config().data


class Entries:
    l: list[Entry]
    id: str

    def __init__(self, data: RawData, id="root"):
        self.id = id
        indices = {}
        for key in Entry.fields():
            param = getattr(Config().data, f"col_{key}")
            try:
                i = data.headers.index(param)
            except ValueError as e:
                raise ConfigurationValueError(
                    "Column name {col_name!r} not found in table {table_name!r}".format(
                        col_name=param, table_name=Config().data.table_name
                    )
                ) from e
            indices[key] = i

        self.l = []
        for row in data.rows:
            try:
                entry = Entry(**{k: row[v] for k, v in indices.items()})
            except ValueError as e:
                logger.warning("invalid entry {row!r} : {error}".format(row=row, error=e))
                continue

            self.l.append(entry)


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


def load_data(loader: DataLoader) -> Entries:
    data = RawData(*loader.load_data(Config().data))
    return Entries(data, "root")
