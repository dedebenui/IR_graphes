from dataclasses import dataclass


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
