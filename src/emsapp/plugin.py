from __future__ import annotations

import importlib
import importlib.util
import os
from pathlib import Path
from typing import Callable, Generic, TypeVar, Union

from emsapp.config import Config
from emsapp.data.loading import DataLoaderFactory
from emsapp.logging import get_logger

logger = get_logger(__name__)

T = TypeVar("T")


class PluginLoadError(ImportError):
    ...


class PlugginInterface(Generic[T]):
    @staticmethod
    def register() -> T:
        ...


def _load_module(mod_descr) -> PlugginInterface:
    mod_path = Path(mod_descr)
    if mod_path.is_file():
        new_mod_name = f"pluggin_{mod_path.stem}"
        spec = importlib.util.spec_from_file_location(new_mod_name, mod_path)
        if spec is None:
            raise PluginLoadError(f"{mod_path} not a python module")

        mod = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(mod)
        except Exception as e:
            raise PluginLoadError(str(e)) from None
        logger.debug(f"loaded module from file {mod_path} as {new_mod_name!r}")
    else:
        mod = importlib.import_module(mod_descr)
        logger.debug(f"Loaded module {mod_descr!r}")
    return mod


def import_plugin(descr: Union[os.PathLike, str], register_fn: Callable[[T], None]):
    mod: PlugginInterface[T] = _load_module(descr)
    try:
        output = mod.register()
    except Exception:
        raise PluginLoadError from None
    register_fn(output)


def load_all_plugins():
    for plugin in Config().plugins.data_loader:
        try:
            import_plugin(plugin, DataLoaderFactory.register)
        except (PluginLoadError, ModuleNotFoundError):
            msg = f"Error while importing {plugin}"
            logger.error(msg, exc_info=True)
            continue
