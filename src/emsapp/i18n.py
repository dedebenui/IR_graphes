import sys
import gettext
from typing import TYPE_CHECKING
import pkg_resources

def N_(s:str)->str:
    return s

if TYPE_CHECKING:

    def _(msg: str) -> str:
        return msg

    def ngettext(msg: str, num: int) -> str:
        return msg
else:
    if sys.platform == "win32":
        import ctypes
        import locale
        windll = ctypes.windll.kernel32
        lang = [locale.windows_locale[windll.GetUserDefaultUILanguage()]]
    else:
        lang = None
    try:
        trans = gettext.translation(
            "messages", pkg_resources.resource_filename("emsapp", "locale"), lang
        )
        _ = trans.gettext
        ngettext = trans.ngettext
    except FileNotFoundError:
        _ = gettext.gettext
        ngettext = gettext.ngettext

