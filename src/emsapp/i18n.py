from typing import Union
import sys
import gettext
from typing import TYPE_CHECKING, Callable
import pkg_resources


def N_(s: str) -> str:
    return s


def get_translation(
    lang: Union[str, list[str]] = None
) -> tuple[Callable[[str], str], Callable[[str, str, int], str]]:
    if isinstance(lang, str):
        lang = [lang]
    elif not lang:
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
    return _, ngettext


if TYPE_CHECKING:

    def _(msg: str) -> str:
        return msg

    def ngettext(msg_sing: str, msg_plur: str, num: int) -> str:
        return msg_sing

else:
    _, ngettext = get_translation()
