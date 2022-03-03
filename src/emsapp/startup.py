import matplotlib
import pkg_resources
import PyQt5
from matplotlib.pyplot import style

from emsapp.data import process
from emsapp.plugin import load_all_plugins

load_all_plugins()
matplotlib.set_loglevel("info")
matplotlib.use("Qt5Agg")
style.use(
    pkg_resources.resource_filename("emsapp", "package_data/default_style.mplstyle")
)
