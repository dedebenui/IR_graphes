from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Protocol, Type, Union

from emsapp import const
from emsapp.config import Config, ConfigurationValueError, DataConfig
from emsapp.logging import get_logger

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

    def import_data(self, config:DataConfig) -> tuple[list[str], list[list]]:
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

    def headers(self, config:DataConfig) -> list[str]:
        """Returns a list of the column names"""
        ...

    def tables(self, config:DataConfig) -> list[str]:
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
    def create(cls, path: Path) -> DataLoader:
        ext = path.suffix.lower()
        return cls._registered[ext](path)

    @classmethod
    def all_extensions(cls) -> list[str]:
        return list(cls._registered)

    @classmethod
    def valid(cls, path: Path) -> bool:
        return path.suffix.lower() in cls._registered


@dataclass
class RawData:
    headers: list[str]
    rows: list[list]


@dataclass
class Entry:
    date_start: datetime
    date_end: datetime
    role: str
    institution: str
    location: str

    def __post_init__(self):
        if self.date_start is None:
            raise ValueError("No start date")
        if self.date_end is None:
            raise ValueError("No end date")


class Entries:
    l: list[Entry]

    def __init__(self, data: RawData):
        indices = {}
        for key, param in zip(
            const.ENTRY_FIELDS,
            [
                Config().data.col_date_start,
                Config().data.col_date_end,
                Config().data.col_role,
                Config().data.col_institution,
                Config().data.col_location,
            ],
        ):
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
