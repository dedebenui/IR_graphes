from __future__ import annotations

from abc import ABC, abstractmethod

from emsapp.config import SplitterConfig
from emsapp.data.loading import Entries
from emsapp.i18n import _
from emsapp.validators import register_valid


class Splitter(ABC):
    name: str
    _registered: dict[str, type[Splitter]] = {}

    @classmethod
    def register(cls, name, new_cls):
        Splitter._registered[name] = new_cls
        register_valid("splitter_type", name)

    @classmethod
    def create(cls, conf: SplitterConfig) -> Splitter:
        cls = Splitter._registered.get(conf.type)
        if cls:
            return cls(conf)

        raise ValueError(
            _("Invalid splitter specifications : {conf!r}").format(conf=conf)
        )

    def __init__(self, conf: SplitterConfig):
        self.name = conf.name

    @abstractmethod
    def __call__(self, entries: Entries) -> list[Entries]:
        ...


class NullSplitter(Splitter):
    def __call__(self, entries: Entries) -> list[Entries]:
        return [entries]


class ColumnSplitter(Splitter):
    def __init__(self, conf: SplitterConfig):
        super().__init__(conf)
        self.col = conf.column

    def __call__(self, entries: Entries) -> list[Entries]:
        out: dict[str, Entries] = {}
        for entry in entries:
            val = getattr(entry, self.col)
            if val not in out:
                new_entries = Entries([], entries.report.copy())
                new_entries.report.splitters[self.name] = val
                out[val] = new_entries
            out[val].l.append(entry)
        return list(out.values())


Splitter.register("value", ColumnSplitter)
