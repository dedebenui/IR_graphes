from __future__ import annotations
from abc import ABC, abstractmethod
from collections import defaultdict
from emsapp.config import GrouperConfig

from emsapp.data import DataReport, DataSet, FinalData, transformers
from emsapp.i18n import _
from emsapp.validators import register_valid


class Grouper(ABC):
    name: str
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
        self.name = conf.name

    @abstractmethod
    def __call__(self, data: list[FinalData]) -> list[DataSet]:
        ...


class StepNameGrouper(Grouper):
    """
    Groups data according to the result of previous splitting and transforming
    steps.
    """

    def __init__(self, conf: GrouperConfig):
        super().__init__(conf)
        self.splitters = set(conf.splitters)
        self.transformers = set(conf.transformers or [])

    def __call__(self, data: list[FinalData]) -> list[DataSet]:
        out: dict[str, list[FinalData]] = defaultdict(list)
        for d in data:
            if self.transformers and d.report.transformer not in self.transformers:
                continue
            key = self.generate_key(d.report)
            out[key].append(d)

        return [DataSet(k, v) for k, v in out.items()]

    def generate_key(self, report: DataReport) -> str:

        splitters = self.splitters or sorted(report.splitters)

        key = (self.name, *(report.splitters[k] for k in splitters))

        return ", ".join(key)


Grouper.register("step_name", StepNameGrouper)
