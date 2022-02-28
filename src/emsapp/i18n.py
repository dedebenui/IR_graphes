import gettext
import locale
import sys
from typing import Protocol, Union
from weakref import WeakValueDictionary

import pkg_resources

AVAILABLE = ["fr", "de"]


class Translatable(Protocol):
    def update_text(self) -> None:
        ...


to_translate: dict[int, Translatable] = WeakValueDictionary()


def register(obj: Translatable):
    global to_translate
    to_translate[id(obj)] = obj
    obj.update_text()


def N_(s: str) -> str:
    return s


def set_lang(lang: Union[str, list[str]] = None):
    global module_gettext, module_ngettext
    if isinstance(lang, str):
        lang = [lang]
    elif not lang:
        if sys.platform == "win32":
            import ctypes

            windll = ctypes.windll.kernel32
            lang = [locale.windows_locale[windll.GetUserDefaultUILanguage()]]
        else:
            lang = None
    locale.setlocale(locale.LC_ALL, lang[0])
    try:
        trans = gettext.translation(
            "messages", pkg_resources.resource_filename("emsapp", "locale"), lang
        )
        module_gettext = trans.gettext
        module_ngettext = trans.ngettext
    except FileNotFoundError:
        module_gettext = gettext.gettext
        module_ngettext = gettext.ngettext
    for obj in to_translate.values():
        obj.update_text()



def _(msg: str) -> str:
    return module_gettext(msg)

def ngettext(msg_sing: str, msg_plur: str, num: int) -> str:
    return module_ngettext(msg_sing, msg_plur, num)

set_lang()
