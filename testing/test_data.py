from emsapp.data_flow.importation import AccessImporter, Entries, Importer
from datetime import datetime


def test_access():
    importer = Importer.create("./testing/testing_data/LocalEMIR.accdb")
    data = importer.to_raw()
    assert data.headers[0] == "id"
    assert data.headers[-1] == "typetest"
    assert isinstance(data.rows[0][1], datetime)


def test_entries():
    importer = Importer.create("./testing/testing_data/LocalEMIR.accdb")
    entries = Entries(importer.to_raw())
    assert entries.l[0].location == "Villars-sous-Mont"
