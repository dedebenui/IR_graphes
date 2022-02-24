from __future__ import annotations
from abc import ABC, abstractmethod
from collections import defaultdict
from emsapp.config import GrouperConfig

from emsapp.data import DataReport, DataSet, FinalData
from emsapp.i18n import _
from emsapp.validators import register_valid


class Grouper(ABC):
    _registered: dict[str, type[Grouper]] = {}

    @classmethod
    def register(cls, name, new_cls):
        Grouper._registered[name] = new_cls
        register_valid("grouper_type", name)

    @classmethod
    def create(cls, conf: GrouperConfig) -> Grouper:
        cls = Grouper._registered.get(conf.type)
        if cls:
            return cls(conf)

        raise ValueError(_("Invalid grouper specifications : {conf!r}").format(conf=conf))

    def __init__(self, conf: GrouperConfig):
        pass

    @abstractmethod
    def __call__(self, data: list[FinalData]) -> list[DataSet]:
        ...


class StepNameGrouper(Grouper):
    """
    Groups data according to the result of previous splitting and transforming
    steps.
    """

    def __init__(self, conf: GrouperConfig):
        self.splitters = set(conf.splitter)
        self.transformers = set(conf.transformer)

    def __call__(self, data: list[FinalData]) -> list[DataSet]:
        out: dict[str, list[FinalData]] = defaultdict(list)
        for d in data:
            key = self.generate_key(d.report)
            out[key].append(d)

        return [DataSet(k, v) for k, v in out.items()]

    def generate_key(self, report: DataReport) -> str:
        if not self.splitters and not self.transformers:
            key = (
                *(report.splitter[k] for k in sorted(report.splitter)),
                *(report.transformer[k] for k in sorted(report.transformer)),
            )
        else:
            key = (
                *(report.splitter[k] for k in self.splitters),
                *(report.transformer[k] for k in self.transformers),
            )
        return ", ".join(key)


Grouper.register("step_name", StepNameGrouper)
