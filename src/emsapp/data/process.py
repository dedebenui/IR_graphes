from dataclasses import dataclass

from emsapp.config import Config
from emsapp.data import DataSet, Entries
from emsapp.data.filters import Filter, create_filter
from emsapp.data.groupers import Grouper, create_grouper
from emsapp.data.splitters import Splitter, create_splitter
from emsapp.data.transformers import Transformer, create_transformer


@dataclass
class Process:
    filters: Filter
    splitters: Splitter
    transformers: dict[str, Transformer]
    grouper: Grouper

    def __call__(self, raw_entries: Entries) -> list[DataSet]:
        filtered_entries = Entries([e for e in raw_entries if all(f(e) for f in self.filters)], "filtered")
        splitted = self.splitter(filtered_entries)
        final_data = [
            trans(entries) for entries in splitted for trans in self.transformers.values()
        ]
        return self.grouper(final_data)


def current_processes() -> dict[str, Process]:
    d: dict[str, Process] = {}

    p_conf = Config().process

    for p_name, config in Config().process.items():
        d[p_name] = Process(
            create_filter(**config.filter),
            create_splitter(**config.splitter),
            {k: create_transformer(**v) for k, v in config.transformer.items()},
            create_grouper(**config.grouper),
        )

    return d
