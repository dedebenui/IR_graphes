from abc import ABC, abstractmethod
import pyodbc
from pathlib import Path


class Importer(ABC):
    @abstractmethod
    def import_data(self) -> tuple[list[str], list[list]]:
        ...


class AccessImporter(Importer):
    def __init__(self, path: Path, table_name: str):
        self.rows = []
        self.path = path
        self.table_name = table_name

    def import_data(self) -> tuple[list[str], list[list]]:
        with pyodbc.connect(
            Rf"Driver={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={self.path};"
        ) as conn:
            cursor = conn.cursor()
            cursor.execute(f"select * from {self.table_name}")
            headers = [column[0] for column in cursor.description]
            self.rows = cursor.fetchall()
        return headers, list(self.rows)
