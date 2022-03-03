from __future__ import annotations

import collections.abc
import json
import os
from collections import defaultdict
from contextlib import contextmanager
from ctypes import Union
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Literal, Optional, TypeVar

import pkg_resources
import tomli
from pydantic import BaseModel, PrivateAttr, confloat

from emsapp.const import (
    PLOT_MAX_HEIGHT,
    PLOT_MAX_WIDTH,
    PLOT_MIN_HEIGHT,
    PLOT_MIN_WIDTH,
)
from emsapp.i18n import N_, _
from emsapp.logging import get_logger
from emsapp.utils import AutoList, auto_repr
from emsapp.validators import column_validator, validate
from emsapp.widgets.common import get_user_input

logger = get_logger()
T = TypeVar("T")


class ConfigurationValueError(ValueError):
    pass


class DataConfig(BaseModel):
    db_path: Path
    table_name: str

    excel_start_year: Literal[1900, 1904]

    col_date_start: str
    col_date_end: str
    col_role: str
    col_institution: str
    col_institution_type: str
    col_location: str

    date_formats: list[str]

    last_selected: str

    @property
    def columns(self) -> list[str]:
        return [
            self.col_date_start,
            self.col_date_end,
            self.col_role,
            self.col_institution,
            self.col_institution_type,
            self.col_location,
        ]


class PluginConfig(BaseModel):
    data_loader: list[str]


class LegendLoc(Enum):
    ABOVE = N_("top")
    AUTO = N_("auto")
    NO_LEGEND = N_("no")


class PlotConfig(BaseModel):
    show_periods_info: bool
    legend_loc: LegendLoc
    plot_height: confloat(ge=PLOT_MIN_HEIGHT, le=PLOT_MAX_HEIGHT)
    plot_width: confloat(ge=PLOT_MIN_WIDTH, le=PLOT_MAX_WIDTH)

    @property
    def figsize(self) -> tuple[float, float]:
        return self.plot_width / 2.54, self.plot_height / 2.54


@auto_repr
class FilterConfig:
    name: str
    type: str
    column: str
    values: list[str] = AutoList(str)

    def __init__(
        self,
        name: str,
        type: str,
        column: str,
        values: list[str] = None,
        value: str = None,
    ):
        self.name = name
        self.type = validate("filter_type", type)
        self.column = column_validator(column)
        self.values = value or values

    @property
    def value(self) -> str:
        return self.values[0]


@auto_repr
class SplitterConfig:
    name: str
    column: str
    type: str = "value"

    def __init__(self, name: str, type: str, column: str):
        self.name = name
        self.type = validate("splitter_type", type)
        self.column = column_validator(column)


@auto_repr
class TransformerConfig:
    name: str
    type: str

    def __init__(self, name: str, type: str):
        self.name = name
        self.type = validate("transformer_type", type)


@auto_repr
class GrouperConfig:
    name: str
    splitters: list[str] = AutoList(str)
    transformers: Optional[list[str]] = AutoList(str, True)
    type: str = "step_name"

    def __init__(
        self,
        name: str,
        splitter: str = None,
        splitters: list[str] = None,
        transformer: str = None,
        transformers: list[str] = None,
    ):
        self.name = name
        self.splitters = splitter or splitters
        self.transformers = transformer or transformers


@dataclass
class ProcessConfig:
    name: str
    filters: dict[str, FilterConfig]
    splitters: dict[str, SplitterConfig]
    transformers: dict[str, TransformerConfig]
    groupers: dict[str, GrouperConfig]

    def __post_init__(self):
        for grp, grouper in self.groupers.items():
            for spl in grouper.splitters:
                if spl not in self.splitters:
                    raise ValueError(
                        _(
                            "splitter {spl} referenced in grouper "
                            "{grp} doesn't exist in process {prc}"
                        ).format(spl=spl, grp=grp, prc=self.name)
                    )
            for trs in grouper.transformers or []:
                if trs not in self.transformers:
                    raise ValueError(
                        _(
                            "transformer {trs} referenced in grouper "
                            "{grp} doesn't exist in process {prc}"
                        ).format(trs=trs, grp=grp, prc=self.name)
                    )

    @classmethod
    def default(cls) -> ProcessConfig:
        return cls.from_file(
            pkg_resources.resource_filename(
                "emsapp", "package_data/default_process.toml"
            )
        )

    @classmethod
    def from_file(cls, path: os.PathLike) -> ProcessConfig:
        with open(path, "rb") as file:
            root = tomli.load(file)

        flt = {n: FilterConfig(name=n, **d) for n, d in root.get("filter", {}).items()}
        spl = {
            n: SplitterConfig(name=n, **d) for n, d in root.get("splitter", {}).items()
        }
        trs = {
            n: TransformerConfig(name=n, **d)
            for n, d in root.get("transformer", {}).items()
        }
        grp = {
            n: GrouperConfig(name=n, **d) for n, d in root.get("grouper", {}).items()
        }
        name = root.get("name", Path(path).stem)
        return cls(name, flt, spl, trs, grp)


class UserData:
    """
    The goal of this class is to store information entered by the user that should never change.
    For example, in which district is located which town.
    """

    d: dict[str, dict[str, str]]

    def __init__(self):
        self.d = defaultdict(dict)
        try:
            with open(
                pkg_resources.resource_filename("emsapp", "package_data/user_data.json")
            ) as file:
                self.d.update(json.load(file))
        except Exception:
            logger.error(
                "could not open user data. Resetting with empty file.", exc_info=True
            )

    def get(
        self,
        value_descr: str,
        key: str,
        validator: Callable[[str], T] = str,
        help_text: str = None,
    ) -> Optional[T]:
        """get a user-provided piece of data. If the data has never been provided before, the user
        is asked to provide it. Otherwise it is recalled from the last time the user provided it.

        Parameters
        ----------
        value_descr : str
            description of the kind of value the user is supposed to enter. Can be thought of
            as a domain.
        key : str
            key to the value
        validator : Callable[[str], T], optional
            Should take a string and return the desired data parsed from the str
            If this function raises a ValueError, the user is given the chance
            to input the data until it is valid or until they cancel, by default str
        help_text : str, optional
            string displayed to help the user know what kind of value to enter. If not provided,
            the docstring of the validator, is specified, is displayed, by default None

        Returns
        -------
        Optional[T]
            the desired data or None if the data is not available and the user cancels.

        Example
        -------
        district = UserData().get("district", "Fribourg") # "Sarine"
        """
        val = self.get_no_ask(value_descr, key, validator)
        if val:
            return val
        return self.ask_user(value_descr, key, validator, help_text)

    def get_no_ask(
        self, value_descr: str, key: str, validator: Callable[[str], T] = str
    ) -> Optional[T]:
        if value_descr in self.d and key in self.d[value_descr]:
            raw_val = self.d[value_descr][key]
            try:
                return validator(raw_val)
            except ValueError:
                logger.warning(
                    f"Could not parse already stored value for {value_descr}:{key} = {raw_val!r}",
                    exc_info=True,
                )
                return None

    def update(self, value_descr: str, key: str, raw_value: str):
        self.d[value_descr][key] = raw_value
        with open(
            pkg_resources.resource_filename("emsapp", "package_data/user_data.json"),
            "w",
        ) as file:
            json.dump(self.d, file, indent=4)

    def ask_user(
        self,
        value_descr: str,
        key: str,
        validator: Callable[[str], T] = str,
        help_text: str = None,
    ) -> Optional[T]:
        msg = _("Please enter a {value_descr} corresponding to {key}").format(
            value_descr=value_descr, key=key
        )
        if help_text:
            msg += "\n" + help_text
        elif validator is not str and validator.__doc__:
            msg += f"\n{validator.__doc__}"
        error_msg = ""
        while True:
            raw_val = get_user_input(f"{msg}\n{error_msg}")
            logger.debug(f"UserData input : {raw_val = }")
            if raw_val is None:
                return raw_val
            try:
                val = validator(raw_val)
            except ValueError as e:
                error_msg = str(e)
                logger.debug(
                    f"invalid value {raw_val} entered by user for {value_descr}:{key}",
                    exc_info=True,
                )
                continue
            break
        self.update(value_descr, key, raw_val)
        return val


class RootConfig(BaseModel):
    data: DataConfig
    plugins: PluginConfig
    plot: PlotConfig
    _process: ProcessConfig = PrivateAttr(default_factory=ProcessConfig.default)
    _user_data: UserData = PrivateAttr(default_factory=UserData)
    _commit_flag: bool = PrivateAttr(True)

    @contextmanager
    def hold(self):
        previous = self.copy(deep=True)
        self._commit_flag = False
        yield
        if not self._commit_flag:
            self.__dict__.update(previous.__dict__)
        else:
            self.save()
        self._commit_flag = True

    def commit(self):
        if self._commit_flag:
            logger.warning("you can only commit when holding")
        else:
            self._commit_flag = True

    def dump(self):
        print(self.json(indent=2))

    def save(self):
        with open(
            pkg_resources.resource_filename(
                "emsapp", "package_data/current_config.json"
            ),
            "w",
        ) as file:
            file.write(self.json(indent=4))

    @property
    def user_data(self) -> UserData:
        return self._user_data

    @property
    def process(self) -> ProcessConfig:
        return self._process


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
        d = deep_update(d, current_config_dict())
        cls.__current = RootConfig(**d)


def default_config_dict() -> dict[str, Any]:
    with open(
        pkg_resources.resource_filename("emsapp", "package_data/default_config.toml"),
        "rb",
    ) as file:
        return tomli.load(file)


def current_config_dict() -> dict[str, Any]:
    try:
        with open(
            pkg_resources.resource_filename(
                "emsapp", "package_data/current_config.json"
            ),
            "r",
        ) as file:
            return json.load(file)
    except (FileNotFoundError, tomli.TOMLDecodeError):
        logger.warning("could not load current config")
        return {}


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
