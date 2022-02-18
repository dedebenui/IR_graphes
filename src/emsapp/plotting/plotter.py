from abc import ABC, abstractmethod
from datetime import datetime


class AbstractPlotter(ABC):
    dates: list[datetime]
    