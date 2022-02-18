from __future__ import annotations

import importlib
import importlib.util
import os
from pathlib import Path
from typing import Generic, Protocol, Type, TypeVar, Union

from emsapp.logging import get_logger

logger = get_logger(__name__)

T = TypeVar("T")


class PluginLoadError(ImportError):
    ...


class PlugginInterface(Generic[T]):
    @staticmethod
    def define_cls(BaseClass: Type[AbstractClass]) -> T:
        ...


class AbstractClass(Protocol, Generic[T]):
    def register(cls, specs: T):
        ...


def _load_module(mod_descr) -> PlugginInterface:
    try:
        mod = importlib.import_module(mod_descr)
        logger.debug(f"Loaded module {mod_descr!r}")
    except (ModuleNotFoundError, TypeError):
        mod_path = Path(mod_descr)

        if not mod_path.is_file():
            raise PluginLoadError(f"{mod_path} is not a file / does not exist")

        new_mod_name = f"pluggin_{mod_path.stem}"
        spec = importlib.util.spec_from_file_location(new_mod_name, mod_path)
        if spec is None:
            raise PluginLoadError(f"{mod_path} not a python module")

        mod = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(mod)
        except Exception:
            msg = f"Error loading {mod_path}"
            logger.error(msg, exc_info=True)
            raise PluginLoadError(msg) from None
        logger.debug(f"loaded module from file {mod_path} as {new_mod_name!r}")
    return mod


def import_plugin(descr: Union[os.PathLike, str], base_class: Type[AbstractClass[T]]):
    mod: PlugginInterface[T] = _load_module(descr)
    try:
        output = mod.define_cls(base_class)
    except Exception:
        msg = f"Error while registering {descr}"
        logger.error(msg, exc_info=True)
        raise PluginLoadError from None

    base_class.register(output)
