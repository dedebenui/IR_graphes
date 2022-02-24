from __future__ import annotations

from dataclasses import dataclass

from emsapp.config import Config
from emsapp.data import DataSet, Entries
from emsapp.data.filters import Filter
from emsapp.data.groupers import Grouper
from emsapp.data.splitters import Splitter
from emsapp.data.transformers import Transformer


@dataclass
class Process:
    filters: list[Filter]
    splitters: list[Splitter]
    transformers: list[Transformer]
    groupers: list[Grouper]

    @classmethod
    def from_config(cls) -> Process:
        p_conf = Config().process

        filters = [Filter.create(conf) for conf in p_conf.filters.values()]
        splitters = [Splitter.create(conf) for conf in p_conf.splitters.values()]
        transformers = [Transformer.create(conf) for conf in p_conf.transformers.values()]
        groupers = [Grouper.create(conf) for conf in p_conf.groupers.values()]

        return Process(filters, splitters, transformers, groupers)

    def __call__(self, raw_entries: Entries) -> list[DataSet]:
        filtered_entries = Entries(
            [e for e in raw_entries if all(f(e) for f in self.filters)], raw_entries.report.copy()
        )
        entries_lists = [filtered_entries]
        for splitter in self.splitters:
            entries_lists = [
                new_entries for entries in entries_lists for new_entries in splitter(entries)
            ]

        final_data = [trans(entries) for entries in entries_lists for trans in self.transformers]
        return [data_set for grouper in self.groupers for data_set in grouper(final_data)]
