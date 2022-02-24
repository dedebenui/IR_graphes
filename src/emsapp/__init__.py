import matplotlib
from emsapp.plugin import load_all_plugins
from emsapp.data import process
import PyQt5

load_all_plugins()
matplotlib.set_loglevel("info")
matplotlib.use("Qt5Agg")