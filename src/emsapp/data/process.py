from dataclasses import dataclass
from emsapp.data import DataSet

from emsapp.data.filters import Filter
from emsapp.data.groupers import Grouper
from emsapp.data.loading import Entries
from emsapp.data.splitters import Splitter
from emsapp.data.transformers import Transformer


@dataclass
class Process:
    filter: Filter
    splitter: Splitter
    transformers: list[Transformer]
    grouper: Grouper

    def __call__(self, raw_entries:Entries)->list[DataSet]:
        filtered_entries = self.filter(raw_entries)
        splitted = self.splitter(filtered_entries)
        final_data = [trans(entries) for entries in splitted for trans in self.transformers]
        return self.grouper(final_data)

