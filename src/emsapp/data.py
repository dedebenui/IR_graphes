from __future__ import annotations
from contextlib import contextmanager

import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterator, Type, Union

import pyodbc

from emsapp.config import Config, ConfigurationValueError
from emsapp.errors import handle_warning
from emsapp import const


class Importer(ABC):
    _registered: dict[str, Type[Importer]] = {}

    def __init_subclass__(cls, ext: Union[str, tuple[str]]):
        if isinstance(ext, str):
            ext = (ext,)
        for e in ext:
            Importer._registered[e] = cls

    @classmethod
    def create(cls, path: Path) -> Importer:
        ext = path.suffix.lower()
        return cls._registered[ext](path)

    @classmethod
    def all_extensions(cls) -> list[str]:
        return list(cls._registered)

    @classmethod
    def valid(cls, path: Path) -> bool:
        return path.suffix.lower() in cls._registered

    @abstractmethod
    def __init__(self, path: Path):
        """creates an importer from a path to a file

        Parameters
        ----------
        path : Path
            path the file containing the data
        """
        ...

    @abstractmethod
    def import_data(self) -> tuple[list[str], list[list]]:
        """imports the whole dataset

        Returns
        -------
        list[str]
            headers (column names)
        list[list]
            list of rows of data. Rows must have the same len as headers
        """
        ...

    @abstractmethod
    def headers(self) -> list[str]:
        """Returns a list of the column names"""
        ...

    @abstractmethod
    def tables(self) -> list[str]:
        """returns a list of available tables"""
        ...

    def to_raw(self) -> RawData:
        return RawData(*self.import_data())


class AccessImporter(Importer, ext=".accdb"):
    def __init__(self, path: Path):
        self.rows = []
        self.path = path

    class Cursor:
        def __init__(_self, path):
            _self.conn = pyodbc.connect(
                Rf"Driver={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={path};"
            )

        def __enter__(self) -> pyodbc.Cursor:
            return self.conn.cursor()

        def __exit__(self, exc_type, exc_val, exc_tb):
            self.conn.close()

    def import_data(self) -> tuple[list[str], list[list]]:
        table_name = Config().data.table_name
        if table_name:
            with self.Cursor(self.path) as cursor:
                try:
                    cursor.execute(f"select * from {table_name}")
                    self.rows = cursor.fetchall()
                    headers = [column[0] for column in cursor.description]
                    return headers, list(self.rows)
                except pyodbc.ProgrammingError:
                    pass
        return [], []

    def headers(self) -> list[str]:
        table_name = Config().data.table_name
        if table_name:
            with self.Cursor(self.path) as cursor:
                try:
                    cursor.execute(f"select * from {table_name}")
                    headers = [column[0] for column in cursor.description]
                    return headers
                except pyodbc.ProgrammingError:
                    pass
        return []

    def tables(self) -> list[str]:
        with self.Cursor(self.path) as cursor:
            return [row.table_name for row in cursor.tables()]


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
                handle_warning("invalid entry {row!r} : {error}".format(row=row, error=e))
                continue

            self.l.append(entry)
