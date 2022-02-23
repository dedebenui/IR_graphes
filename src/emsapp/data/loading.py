from __future__ import annotations

import os
from pathlib import Path
from typing import Protocol, Union

from emsapp.config import Config, ConfigurationValueError, DataConfig
from emsapp.data import Entries, Entry, RawData
from emsapp.logging import get_logger
from emsapp.i18n import _

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
    _registered: dict[str, type[DataLoader]] = {}

    @classmethod
    def register(cls, specs: tuple[Union[str, tuple[str]], type[DataLoader]]):
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


def load_data(loader: DataLoader = None) -> Entries:
    loader = loader or DataLoaderFactory.create(Config().data.db_path)
    data = RawData(*loader.load_data(Config().data))
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

    l = []
    for row in data.rows:
        try:
            entry = Entry(**{k: row[v] for k, v in indices.items()})
            if (t := entry.institution_type) and t.lower() != "ems":
                continue
        except ValueError as e:
            logger.warning("invalid entry {row!r} : {error}".format(row=row, error=e))
            continue

        l.append(entry)
    return Entries(l, "root")
