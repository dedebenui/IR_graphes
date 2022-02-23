from abc import ABC, abstractmethod
from collections import defaultdict
from emsapp.config import GrouperConfig

from emsapp.data import DataSet, FinalData
from emsapp.i18n import _


class Grouper(ABC):
    @abstractmethod
    def __call__(self, data: list[FinalData]) -> list[DataSet]:
        ...


class NullGrouper(Grouper):
    def __call__(self, data: list[FinalData]) -> list[DataSet]:
        return [DataSet(_("ungrouped"), [d]) for d in data]


class ColumnGrouper(Grouper):
    def __call__(self, data: list[FinalData]) -> list[DataSet]:
        out: dict[str, list[FinalData]] = defaultdict(list)
        for d in data:
            out[d.specs.get("value")].append(d)

        return [DataSet(k, v) for k, v in out.items()]


def create_grouper(conf: GrouperConfig):

    if type == "value":
        return ColumnGrouper()

    raise ValueError("Invalid grouper specifications")
