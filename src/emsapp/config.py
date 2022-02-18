from __future__ import annotations
from contextlib import contextmanager

import os
from pathlib import Path
from typing import Any, Iterator

import pkg_resources
import tomli
from pydantic import BaseModel, PrivateAttr

import collections.abc

from emsapp.logging import get_logger

logger = get_logger()


class ConfigurationValueError(ValueError):
    pass


class DataConfig(BaseModel):
    db_path: Path
    table_name: str

    col_date_start: str
    col_date_end: str
    col_role: str
    col_institution: str
    col_location: str

    @property
    def columns(self) -> list[str]:
        return [
            self.col_date_start,
            self.col_date_end,
            self.col_role,
            self.col_institution,
            self.col_location,
        ]


class PluginConfig(BaseModel):
    data_loader: list[str]



class RootConfig(BaseModel):
    data: DataConfig
    plugins: PluginConfig
    _commit_flag: bool = PrivateAttr(True)

    @contextmanager
    def hold(self):
        previous = self.copy(deep=True)
        self._commit_flag = False
        yield
        if not self._commit_flag:
            self.__dict__.update(previous.__dict__)
        self._commit_flag = True

    def commit(self):
        if self._commit_flag:
            logger.warning("you can only commit when holding")
        else:
            self._commit_flag = True

    def dump(self):
        print(self.json(indent=2))


class Config:
    __current: RootConfig = None

    def __new__(cls) -> RootConfig:
        if cls.__current is None:
            cls.reload()
        return cls.__current

    @classmethod
    def reload(cls, path: os.PathLike = None):
        """
        This is where the configuration is loaded.
        Paths are searched for a valid config in this order :
            - provided path
            - packaged default config
        """
        d = default_config_dict()
        cls.__current = RootConfig(**d)


def default_config_dict() -> dict[str, Any]:
    with open(pkg_resources.resource_filename("emsapp", "defaults/config.toml"), "rb") as file:
        return tomli.load(file)


def deep_update(d: collections.abc.Mapping, u: collections.abc.Mapping):
    for k, v in u.items():
        if isinstance(v, collections.abc.Mapping):
            d[k] = deep_update(d.get(k, {}), v)
        else:
            d[k] = v
    return d


if __name__ == "__main__":
    c1 = Config()
    c2 = Config()
    print(c1 is c2)
    print(c1)
    print(Config().data.col_institution)
