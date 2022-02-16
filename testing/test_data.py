from emsapp.data import AccessImporter
from datetime import datetime


def test_access():
    importer = AccessImporter("./testing/testing_data/LocalEMIR.accdb", "ci")
    headers, data = importer.import_data()
    assert headers[0] == "id"
    assert headers[-1] == "typetest"
    assert isinstance(data[0][1], datetime)


test_access()
