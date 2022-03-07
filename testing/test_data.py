from emsapp.config import Config
from emsapp.data.loading import Entries, DataLoaderFactory, RawData
from datetime import date


def test_access():
    importer = DataLoaderFactory.create("./testing/testing_data/LocalEMIR.accdb")
    data = RawData(*importer.load_data(Config().data))
    assert data.headers[0] == "id"
    assert data.headers[-1] == "typetest"
    assert isinstance(data.rows[0][1], date)


def test_entries():
    importer = DataLoaderFactory.create("./testing/testing_data/LocalEMIR.accdb")
    data = RawData(*importer.load_data(Config().data))
    entries = Entries(data)
    assert entries.l[0].location == "Villars-sous-Mont"
