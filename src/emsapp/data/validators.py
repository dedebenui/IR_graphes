from emsapp.const import DISTRICTS
from emsapp.i18n import _

def district_validator(s:str)->str:
    if s.title() in DISTRICTS:
        return s.title()
    raise ValueError(_("{s} does not appear in {district_list!r}").format(s=s, district_list=DISTRICTS))