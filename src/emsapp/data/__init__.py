from dataclasses import dataclass
from enum import Enum
from pydoc import describe
from typing import Any, Iterator
from dataclasses import field
import numpy as np


class DataType(Enum):
    LINE="line"
    BAR="bar"
    PERIOD="period"


@dataclass
class RawData:
    headers: list[str]
    rows: list[list]


@dataclass
class FinalData:
    x:np.ndarray
    y:np.ndarray
    data_type:DataType
    
    id:str
    description:str
    specs:dict[str, str]
    extra_data:dict[str, Any] = field(default_factory=dict)



@dataclass
class DataSet:
    title:str
    data:list[FinalData]

    def __iter__(self)->Iterator[FinalData]:
        yield from self.data
