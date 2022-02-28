import datetime
import io
import itertools
from collections import defaultdict
from enum import Enum
from emsapp.const import COLORS, DATE_OUTPUT_FMT

from emsapp.data import DataSet, DataType, FinalData
from emsapp.i18n import _, ngettext
from matplotlib import pyplot as plt
import matplotlib.dates as mdates


class PlotType(Enum):
    LINE = "line"
    BAR = "bar"
    PERIOD = "period"
    MIXED = "mixed"


class DateFormatter:
    def __call__(self, x, pos=0):
        return _(DATE_OUTPUT_FMT).format(dt=mdates.num2date(x))


class Plotter:
    title: str
    data: dict[DataType, list[FinalData]]
    plot_type: PlotType
    legend_handles: list[plt.Artist]
    legend_labels: list[str]

    def __init__(self, data_set: DataSet, ax: plt.Axes = None):
        self.indices: dict[DataType, int] = defaultdict(int)
        self.legend_handles = []
        self.legend_labels = []
        if ax:
            self.ax = ax
            self.fig = self.ax.get_figure()
        else:
            self.fig, self.ax = plt.subplots()
        self.color_cycle = itertools.cycle(COLORS)
        self.title = data_set.title
        self.data = defaultdict(list)
        tpe = self.plot_type = PlotType.MIXED
        for data in data_set:
            self.data[data.data_type].append(data)
            tpe = data.data_type.value
        if len(self.data) == 1:
            self.plot_type = PlotType(tpe)
        self.plot()

    def as_bytes(self) -> bytes:
        with io.BytesIO() as buffer:
            self.fig.savefig(buffer, bbox_inches="tight", format="png", dpi=200)
            return buffer.getvalue()

    def plot(self):
        for tpe, datas in self.data.items():
            if tpe == DataType.LINE:
                self.plot_lines(datas)
            elif tpe == DataType.BAR:
                self.plot_bars(datas)
            elif tpe == DataType.PERIOD:
                self.plot_periods(datas)
        self.ax.relim()
        self.ax.autoscale()
        self.fmt_xaxis()

    def fmt_xaxis(self):
        locator = mdates.WeekdayLocator(byweekday=mdates.MONDAY)
        formatter = DateFormatter()
        self.ax.xaxis.set_major_locator(locator)
        self.ax.xaxis.set_major_formatter(formatter)
        self.ax.xaxis.set_minor_locator(mdates.DayLocator())
        self.fig.autofmt_xdate()

    def plot_lines(self, data_list: list[FinalData]):
        """plots all available lines.

        Parameters
        ----------
        data : FinalData
            data as returned by a Transformer
        """
        for data in data_list:
            (l,) = self.ax.plot(data.x, data.y, color=next(self.color_cycle))
            self.legend_handles.append(l)
            self.legend_labels.append(data.description)

    def plot_bars(self, data_list: list[FinalData]):
        """plots some bars

        Parameters
        ----------
        data : FinalData
            data as returned by a Transformer
        """
        n = len(data_list)
        total_width = datetime.timedelta(1)
        offset = total_width / n
        start = 0.5 * (-total_width + offset)
        for i, data in enumerate(data_list):
            cont = self.ax.bar(
                data.x + start + i * offset, data.y, offset, color=next(self.color_cycle)
            )
            self.legend_handles.append(cont.patches[0])
            self.legend_labels.append(data.description)

    def plot_periods(self, data_list: list[FinalData]):
        """plots some periods

        Parameters
        ----------
        data : FinalData
            data as returned by a Transformer
        """
        if len(data_list) == 1:
            data = data_list[0]
            for start, end, ppl in zip(data.x[::2], data.x[1::2], data.y[::2]):
                s = fmt_period(start, end, ppl)
                (l,) = self.ax.plot(
                    [start, end],
                    [0.6, 0.6],
                    transform=self.ax.get_xaxis_transform(),
                    label=data.description,
                    c="k",
                )
                self.ax.plot(
                    [start, start], [0.55, 0.65], c="k", transform=self.ax.get_xaxis_transform()
                )
                self.ax.plot(
                    [end, end], [0.55, 0.65], c="k", transform=self.ax.get_xaxis_transform()
                )
            self.legend_handles.append(l)
            self.legend_labels.append(data.description)


def fmt_period(start: datetime.datetime, end: datetime.datetime, people: int) -> str:
    num_days = (end - start).days + 1
    days = ngettext("{} day", "{} days", num_days).format(num_days)
    ppl = ngettext("{} person", "{} people", people).format(people)
    return f"{start} - {end} ({days}, {ppl})"
