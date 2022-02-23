from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable
from emsapp.config import Config, FilterConfig
from emsapp.data.loading import Entries, Entry
from emsapp.i18n import _

registered: dict[str, type[Filter]] = {}


class Filter(ABC):
    @classmethod
    def create(conf: FilterConfig) -> Filter:
        cls = registered.get(conf.type)
        if cls:
            return cls(conf)

        raise ValueError(_("Invalid filter specifications : {conf!r}").format(conf=conf))

    @abstractmethod
    def __init__(self, conf: FilterConfig):
        ...

    @abstractmethod
    def __call__(self, entry: Entry) -> bool:
        ...


class IncludeFilter(Filter):
    def __init__(self, conf: FilterConfig):
        self.col = conf.column
        self.val = set(conf.values)
        if conf.column not in Entry.fields():
            raise ValueError(f"Can only filter existing columns : {Entry.fields()!r}")

    def __call__(self, entry: Entry) -> bool:
        return getattr(entry, self.col) in self.val


class ExcludeFilter(Filter):
    def __init__(self, conf: FilterConfig):
        self.col = conf.column
        self.val = set(conf.values)
        if conf.column not in Entry.fields():
            raise ValueError(f"Can only filter existing columns : {Entry.fields()!r}")

    def __call__(self, entry: Entry) -> bool:
        return getattr(entry, self.col) not in self.val


class ExcludeFilter(Filter):
    def __init__(self, conf: FilterConfig):
        self.col = conf.column
        self.val = set(conf.values)
        if conf.column not in Entry.fields():
            raise ValueError(f"Can only filter existing columns : {Entry.fields()!r}")

    def __call__(self, entry: Entry) -> bool:
        return getattr(entry, self.col) not in self.val
