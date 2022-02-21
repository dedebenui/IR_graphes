from abc import ABC, abstractmethod

from emsapp.data.loading import Entries


class Splitter(ABC):
    @abstractmethod
    def __call__(self, entries: Entries) -> list[Entries]:
        ...
