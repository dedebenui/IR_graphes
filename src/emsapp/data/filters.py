from __future__ import annotations

from abc import ABC, abstractmethod
from emsapp.config import Config
from emsapp.data.loading import Entries, Entry


class Filter(ABC):
    @abstractmethod
    def __call__(self, entry: Entry) -> bool:
        ...

    def __and__(self, other: Filter) -> CombinedAndFilter:
        return CombinedAndFilter(self, other)

    def __or__(self, other: Filter) -> CombinedOrFilter:
        return CombinedOrFilter(self, other)


class CombinedFilter(Filter):
    def __init__(self, filter_a: Filter, filter_b: Filter):
        self.filter_a = filter_a
        self.filter_b = filter_b


class CombinedAndFilter(CombinedFilter):
    def __call__(self, entry: Entry) -> bool:
        return self.filter_a(entry) and self.filter_b(entry)


class CombinedOrFilter(CombinedFilter):
    def __call__(self, entry: Entry) -> bool:
        return self.filter_a(entry) or self.filter_b(entry)


class NullFilter(Filter):
    def __call__(self, entry: Entry) -> bool:
        return True


class NotFilter(Filter):
    def __init__(self, filter: Filter):
        self.filter = filter

    def __call__(self, entry: Entry) -> bool:
        return not self.filter(entry)


class ColumnFilter(Filter):
    def __init__(self, column: str, value: str):
        self.col = column
        self.val = value
        if column not in Entry.fields():
            raise ValueError(f"Can only filter existing columns : {Entry.fields()!r}")

    def __call__(self, entry: Entry) -> bool:
        return getattr(entry, self.col) == self.val


def create_filter(type: str = None, column: str = None, value: str = None) -> Filter:
    if not type:
        return NullFilter()
    if type == "include":
        return ColumnFilter(column, value)

    raise ValueError("Invalid filter specifications")
