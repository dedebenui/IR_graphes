from dataclasses import dataclass
import json
from typing import Any
from pkg_resources import resource_filename




@dataclass
class RawData:
    headers: list[str]
    rows: list[list]


@dataclass
class FinalData:
    ...


@dataclass
class DataSet:
    ...
