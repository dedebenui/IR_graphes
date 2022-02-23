from abc import ABC, abstractmethod
from collections import defaultdict
from datetime import datetime, timedelta

import numpy as np

from emsapp.data import DataType, FinalData
from emsapp.data.loading import Entries, Entry
from emsapp.i18n import _


class Transformer(ABC):
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

        min_date = datetime.today()
        max_date = datetime.today()

        for entry in entries:
            date = entry.date_start
            min_date = min(min_date, date)
            max_date = max(max_date, date)
            cases[date] += 1

        x = [min_date + timedelta(d) for d in range((max_date - min_date).days + 1)]
        y = [cases[d] for d in x]
        return FinalData(
            np.array(x),
            np.array(y),
            DataType.BAR,
            id="new:" + entries.id,
            description=_("New cases"),
            specs=entries.specs,
        )


class CumulativeTransformer(Transformer):
    def __call__(self, entries: Entries) -> FinalData:
        """
        transforms data to show how many people were isolated on a particular date
        """
        cases = defaultdict(int)

        min_date = datetime.today()
        max_date = datetime.today()

        for entry in entries:
            start = entry.date_start
            end = entry.date_end
            min_date = min(min_date, start)
            max_date = max(max_date, end)
            for d in range((end - start).days + 1):
                cases[start + timedelta(d)] += 1

        x = [min_date + timedelta(d) for d in range((max_date - min_date).days + 1)]
        y = [cases[d] for d in x]
        return FinalData(
            np.array(x),
            np.array(y),
            DataType.LINE,
            id="cumulative:" + entries.id,
            description=_("People in confinment"),
            specs=entries.specs,
        )


class PeriodTransformer(Transformer):
    def __call__(self, entries: Entries) -> FinalData:
        """
        Tranforms entries into data representing periods of outbreaks.
        """
        dur = timedelta(9)

        sorted_entries = sorted(entries.l, key=lambda en: en.date_start)
        x = []
        y = []

        periods: list[list[Entry]] = []

        start = sorted_entries[0].date_start
        curr_end = start + dur
        entry_list = [sorted_entries[0]]
        for entry in sorted_entries:
            if entry.date_start <= curr_end:
                entry_list.append(entry)
                curr_end = entry.date_start + dur
            else:
                x += [start, curr_end]
                y += [len(entry_list)] * 2
                periods.append(entry_list)
                start = entry.date_start
                curr_end = start + dur
                entry_list = [entry]
        periods.append(entry_list)
        x += [start, curr_end]
        y += [len(entry_list)] * 2
        return FinalData(
            np.array(x),
            np.array(y),
            DataType.PERIOD,
            id="period:" + entries.id,
            description=_("Period in question"),
            specs=entries.specs,
        )


def create_transformer(type: str):
    if type == "periods":
        return PeriodTransformer()
    elif type == "new":
        return NewTransformer()
    elif type == "cumulative":
        return CumulativeTransformer()

    raise ValueError("Invalid transformer specifications")
