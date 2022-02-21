from abc import ABC, abstractmethod

from emsapp.data import FinalData
from emsapp.data.loading import Entries


class Transformer(ABC):
    @abstractmethod
    def __call__(self, entries:Entries)->FinalData:
        ...
