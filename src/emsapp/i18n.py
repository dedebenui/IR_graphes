import gettext
from typing import TYPE_CHECKING
import pkg_resources

import emsapp.const

if TYPE_CHECKING:

    def _(msg: str) -> str:
        return msg

    def ngettext(msg: str, num: int) -> str:
        return msg
else:
    trans = gettext.translation(
        "messages", pkg_resources.resource_filename("emsapp", "locale"), ["fr"]
    )
    _ = trans.gettext
    ngettext = trans.ngettext

