import sys
import traceback

from PyQt5 import QtCore, QtWidgets

from emsapp.i18n import _
from emsapp.utils import get_logger
from emsapp.widgets.info_box import InfoBox

logger = get_logger(__name__)


def show_exception_box(log_msg):
    """Checks if a QApplication instance is available and shows a messagebox with the exception message.
    If unavailable (non-console application), log an additional notice.
    """
    if QtWidgets.QApplication.instance() is not None:
        errorbox = InfoBox(_("Oops. An unexpected error occured:"), log_msg)
        errorbox.exec()
    else:
        logger.debug("No QApplication instance available.")


class UncaughtHook(QtCore.QObject):
    _exception_caught = QtCore.pyqtSignal(object)

    def __init__(self, *args, **kwargs):
        super(UncaughtHook, self).__init__(*args, **kwargs)

        # this registers the exception_hook() function as hook with the Python interpreter
        sys.excepthook = self.exception_hook

        # connect signal to execute the message box function always on main thread
        self._exception_caught.connect(show_exception_box)

    def exception_hook(self, exc_type, exc_value, exc_traceback):
        """Function handling uncaught exceptions.
        It is triggered each time an uncaught exception occurs.
        """
        if issubclass(exc_type, KeyboardInterrupt):
            # ignore keyboard interrupt to support console applications
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
        else:
            exc_info = (exc_type, exc_value, exc_traceback)
            log_msg = "\n".join(
                [
                    "".join(traceback.format_tb(exc_traceback)),
                    "{0}: {1}".format(exc_type.__name__, exc_value),
                ]
            )
            logger.critical(
                "Uncaught exception:\n {0}".format(log_msg), exc_info=exc_info
            )

            # trigger message box show
            self._exception_caught.emit(log_msg)


# create a global instance of our class to register the hook
qt_exception_hook = UncaughtHook()
