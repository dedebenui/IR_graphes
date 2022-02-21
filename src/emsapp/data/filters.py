from abc import ABC, abstractmethod
from emsapp.data.loading import Entries

class Filter(ABC):
    @abstractmethod
    def __call__(self, entries:Entries)->Entries:
        ...