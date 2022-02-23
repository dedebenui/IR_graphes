from abc import ABC, abstractmethod
from emsapp.config import SplitterConfig

from emsapp.data.loading import Entries, Entry


class Splitter(ABC):
    @abstractmethod
    def __call__(self, entries: Entries) -> list[Entries]:
        ...


class NullSplitter(Splitter):
    def __call__(self, entries: Entries) -> list[Entries]:
        return [entries]


class ColumnSplitter(Splitter):
    def __init__(self, column: str):
        self.col = column
        if column not in Entry.fields():
            raise ValueError(f"Can only split with existing columns : {Entry.fields()!r}")

    def __call__(self, entries: Entries) -> list[Entries]:
        out: dict[str, Entries] = {}
        for entry in entries:
            val = getattr(entry, self.col)
            if val not in out:
                out[val] = Entries(
                    [], id=val, specs=entries.specs | dict(column=self.col, value=val)
                )
            out[val].l.append(entry)
        return list(out.values())


def create_splitter(conf:SplitterConfig):
    if conf.type == "value":
        return ColumnSplitter(conf.column)
    elif conf.type == "date":
        raise NotImplementedError()

    raise ValueError("Invalid splitter specifications")
