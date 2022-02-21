from abc import ABC, abstractmethod

from emsapp.data import DataSet, FinalData


class Grouper(ABC):
    @abstractmethod
    def __call__(self, data: list[FinalData]) -> list[DataSet]:
        ...
