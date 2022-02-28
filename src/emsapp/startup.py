import matplotlib
from matplotlib.pyplot import style
import pkg_resources
from emsapp.plugin import load_all_plugins
from emsapp.data import process
import PyQt5

load_all_plugins()
matplotlib.set_loglevel("info")
matplotlib.use("Qt5Agg")
style.use(pkg_resources.resource_filename("emsapp", "package_data/default_style.mplstyle"))