from pathlib import Path

import pyodbc


class AccessDataLoader:
    class Cursor:
        def __init__(_self, path):
            _self.conn = pyodbc.connect(
                Rf"Driver={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={path};"
            )

        def __enter__(self) -> pyodbc.Cursor:
            return self.conn.cursor()

        def __exit__(self, exc_type, exc_val, exc_tb):
            self.conn.close()
            if exc_type is pyodbc.ProgrammingError:
                return True

    def __init__(self, path: Path):
        self.rows = []
        self.path = path
        self.all_tables: dict[str, list[str]] = {}
        with self.Cursor(self.path) as cursor:
            tables = [row.table_name for row in cursor.tables()]
            for table in tables:
                try:
                    cursor.execute(f"select * from {table}")
                    headers = [column[0] for column in cursor.description]
                except pyodbc.ProgrammingError:
                    continue
                self.all_tables[table] = headers

    def load_data(self, config) -> tuple[list[str], list[list]]:
        table_name = config.table_name
        if table_name in self.all_tables:
            with self.Cursor(self.path) as cursor:
                cursor.execute(f"select * from {table_name}")
                self.rows = cursor.fetchall()
                headers = [column[0] for column in cursor.description]
                return headers, list(self.rows)
        return [], []

    def headers(self, config) -> list[str]:
        table_name = config.table_name
        return self.all_tables.get(table_name, [])

    def tables(self, config) -> list[str]:
        return list(self.all_tables)


def register():
    return ".accdb", AccessDataLoader
