from emsapp.const import ALL_COLUMNS, DISTRICTS
from emsapp.i18n import _

def district_validator(s:str)->str:
    if s.title() in DISTRICTS:
        return s.title()
    raise ValueError(_("{s} does not appear in {district_list!r}").format(s=s, district_list=DISTRICTS))


def column_validator(s:str):
    if s not in ALL_COLUMNS:
        raise ValueError(f"{s} is not a valid column. Possible values : {ALL_COLUMNS!r}")
    return s