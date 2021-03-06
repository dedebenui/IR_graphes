from __future__ import annotations

import datetime
from abc import ABC, abstractmethod
from collections import defaultdict

import numpy as np

from emsapp.config import TransformerConfig
from emsapp.data import DataType, FinalData
from emsapp.data.loading import Entries, Entry
from emsapp.i18n import N_, _
from emsapp.validators import register_valid


class Transformer(ABC):
    name: str
    _registered: dict[str, type[Transformer]] = {}

    @classmethod
    def register(cls, name, new_cls):
        Transformer._registered[name] = new_cls
        register_valid("transformer_type", name)

    @classmethod
    def create(cls, conf: TransformerConfig) -> Transformer:
        cls = Transformer._registered.get(conf.type)
        if cls:
            return cls(conf)

        raise ValueError(
            _("Invalid transformer specifications : {conf!r}").format(conf=conf)
        )

    def __init__(self, conf: TransformerConfig):
        self.name = conf.name

    @abstractmethod
    def __call__(self, entries: Entries) -> FinalData:
        ...


class NewTransformer(Transformer):
    def __call__(self, entries: Entries) -> FinalData:
        """
        transforms entries into data representing how many new cases occur
        on a particuar date.
        """
        cases = defaultdict(int)

        min_date = datetime.date.today()
        max_date = datetime.date.today()

        for entry in entries:
            date = entry.date_start
            min_date = min(min_date, date)
            max_date = max(max_date, date)
            cases[date] += 1

        x = [
            min_date + datetime.timedelta(d)
            for d in range((max_date - min_date).days + 1)
        ]
        y = [cases[d] for d in x]

        report = entries.report.copy()
        report.transformer = self.name

        return FinalData(
            np.array(x),
            np.array(y),
            DataType.BAR,
            description=N_("New cases"),
            report=report,
        )


class CumulativeTransformer(Transformer):
    def __call__(self, entries: Entries) -> FinalData:
        """
        transforms data to show how many people were isolated on a particular date
        """
        cases = defaultdict(int)

        min_date = datetime.date.today()
        max_date = datetime.date.today()

        for entry in entries:
            start = entry.date_start
            end = entry.date_end
            min_date = min(min_date, start)
            max_date = max(max_date, end)
            for d in range((end - start).days + 1):
                cases[start + datetime.timedelta(d)] += 1

        x = (
            [min_date - datetime.timedelta(1)]
            + [
                min_date + datetime.timedelta(d)
                for d in range((max_date - min_date).days + 1)
            ]
            + [max_date + datetime.timedelta(1)]
        )
        y = [cases[d] for d in x]

        report = entries.report.copy()
        report.transformer = self.name

        return FinalData(
            np.array(x),
            np.array(y),
            DataType.LINE,
            description=N_("People in confinment"),
            report=report,
        )


class PeriodTransformer(Transformer):
    def __call__(self, entries: Entries) -> FinalData:
        """
        Tranforms entries into data representing periods of outbreaks.
        """
        dur = datetime.timedelta(9)

        sorted_entries = sorted(entries.l, key=lambda en: en.date_start)
        x = []
        y = []

        periods: list[list[Entry]] = []

        start = sorted_entries[0].date_start
        curr_end = start + dur
        entry_list = [sorted_entries[0]]
        for entry in sorted_entries[1:]:
            if entry.date_start <= curr_end:
                entry_list.append(entry)
                curr_end = entry.date_start + dur
            else:
                periods.append(entry_list)
                x += [start, curr_end]
                y += [len(entry_list)] * 2
                start = entry.date_start
                curr_end = start + dur
                entry_list = [entry]
        periods.append(entry_list)
        x += [start, curr_end]
        y += [len(entry_list)] * 2

        report = entries.report.copy()
        report.transformer = self.name

        return FinalData(
            np.array(x),
            np.array(y),
            DataType.PERIOD,
            description=N_("Period in question"),
            report=report,
        )


Transformer.register("new", NewTransformer)
Transformer.register("cumulative", CumulativeTransformer)
Transformer.register("periods", PeriodTransformer)
