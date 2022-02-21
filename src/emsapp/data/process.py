from dataclasses import dataclass
from emsapp.config import Config, ProcessConfig
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
    transformers: dict[str, Transformer]
    grouper: Grouper

    @classmethod
    def from_config(cls, config: ProcessConfig):
        return cls()

    def __call__(self, raw_entries: Entries) -> list[DataSet]:
        filtered_entries = Entries([e for e in raw_entries if self.filter(e)], "filtered")
        splitted = self.splitter(filtered_entries)
        final_data = [
            trans(entries) for entries in splitted for trans in self.transformers.values()
        ]
        return self.grouper(final_data)


def current_process() -> list[Process]:
    config = Config().process
