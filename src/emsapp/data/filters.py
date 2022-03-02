from __future__ import annotations

from abc import ABC, abstractmethod
from emsapp.config import FilterConfig
from emsapp.data import Entry, parse_date
from emsapp.validators import register_valid
from emsapp.i18n import _


class Filter(ABC):
    name: str
    _registered: dict[str, type[Filter]] = {}

    @classmethod
    def register(cls, name, new_cls):
        Filter._registered[name] = new_cls
        register_valid("filter_type", name)

    @classmethod
    def create(cls, conf: FilterConfig) -> Filter:
        cls = Filter._registered.get(conf.type)
        if cls:
            return cls(conf)

        raise ValueError(
            _("Invalid filter specifications : {conf!r}").format(conf=conf)
        )

    def __init__(self, conf: FilterConfig):
        self.name = conf.name

    @abstractmethod
    def __call__(self, entry: Entry) -> bool:
        ...


class NullFilter(Filter):
    def __call__(self, entry: Entry) -> bool:
        return True


class ValueFilter(Filter):
    def __init__(self, conf: FilterConfig):
        super().__init__(conf)
        self.col = conf.column
        self.val = set(conf.values)


class IncludeFilter(ValueFilter):
    def __call__(self, entry: Entry) -> bool:
        return getattr(entry, self.col) in self.val


class ExcludeFilter(ValueFilter):
    def __call__(self, entry: Entry) -> bool:
        return getattr(entry, self.col) not in self.val


class DateFilter(Filter):
    def __init__(self, conf: FilterConfig):
        super().__init__(conf)
        self.col = conf.column
        self.val = parse_date(conf.value)


class DateBeforeFilter(DateFilter):
    def __call__(self, entry: Entry) -> bool:
        return getattr(entry, self.col) <= self.val


class DateAfterFilter(DateFilter):
    def __call__(self, entry: Entry) -> bool:
        return getattr(entry, self.col) >= self.val


Filter.register("include", IncludeFilter)
Filter.register("exclude", ExcludeFilter)
Filter.register("date_before", DateBeforeFilter)
Filter.register("date_after", DateAfterFilter)
