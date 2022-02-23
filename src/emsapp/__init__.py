import matplotlib
from emsapp.plugin import load_all_plugins
import PyQt5

load_all_plugins()
matplotlib.set_loglevel("info")
matplotlib.use("Qt5Agg")