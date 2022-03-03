import datetime
import io
import itertools
from collections import defaultdict
from enum import Enum

import matplotlib.dates as mdates
from matplotlib import pyplot as plt
from matplotlib.ticker import MaxNLocator

from emsapp.config import Config, LegendLoc
from emsapp.const import COLORS, DATE_OUTPUT_FMT
from emsapp.data import DataSet, DataType, FinalData
from emsapp.i18n import _, ngettext


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
    _extra_info: list[str]
    _sec_ax = None

    def __init__(self, data_set: DataSet, ax: plt.Axes = None):
        self.indices: dict[DataType, int] = defaultdict(int)
        self.legend_handles = []
        self.legend_labels = []
        self._extra_info = []
        if ax:
            self.ax = ax
            self.fig = self.ax.get_figure()
        else:
            self.fig, self.ax = plt.subplots(figsize=Config().plot.figsize)
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

    @property
    def extra_info(self) -> str:
        return "\n".join(self._extra_info)

    def secondary_axis(self) -> plt.Axes:
        if not self._sec_ax:
            self._sec_ax = self.ax.secondary_xaxis("top")
        return self._sec_ax

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
        self.legend(Config().plot.legend_loc)
        if self.plot_type is not PlotType.PERIOD:
            self.ax.yaxis.set_major_locator(MaxNLocator(integer=True))
        if Config().plot.show_today:
            today = datetime.date.today()
            self.ax.axvline(
                datetime.datetime(today.year, today.month, today.day), c="r", lw=2
            )
        self.ax.relim()
        self.ax.autoscale()
        self.fmt_xaxis()

    def legend(self, loc: LegendLoc):
        if loc == LegendLoc.ABOVE:
            self.ax.legend(
                self.legend_handles,
                self.legend_labels,
                bbox_to_anchor=(0, 1.02, 1, 0.2),
                ncol=3,
                loc="lower left",
                mode="expand",
            )
        elif loc == LegendLoc.AUTO:
            self.ax.legend(self.legend_handles, self.legend_labels)

    def fmt_xaxis(self):
        start, end = self.ax.get_xlim()
        duration = (mdates.num2date(end) - mdates.num2date(start)).days + 1
        formatter = DateFormatter()
        monday_loc = mdates.WeekdayLocator(byweekday=mdates.MONDAY)
        if duration > 180:
            self.ax.xaxis.set_major_locator(mdates.MonthLocator(bymonthday=(1, 15)))
            self.ax.xaxis.set_major_formatter(formatter)
        else:
            self.ax.xaxis.set_major_locator(monday_loc)
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
            if self.plot_type == PlotType.MIXED:
                self.legend_labels.append(_(data.description))
            else:
                self.legend_labels.append(data.report.final_label)

    def plot_bars(self, data_list: list[FinalData]):
        """plots some bars

        Parameters
        ----------
        data : FinalData
            data as returned by a Transformer
        """
        n = len(data_list)
        total_width = datetime.timedelta(1) / 1.1
        offset = total_width / n
        start = 0.5 * (-total_width + offset)
        for i, data in enumerate(data_list):
            cont = self.ax.bar(
                data.x + start + i * offset,
                data.y,
                offset,
                color=next(self.color_cycle),
            )
            self.legend_handles.append(cont.patches[0])
            self.legend_labels.append(_(data.description))

    def plot_periods(self, data_list: list[FinalData]):
        """plots some periods

        Parameters
        ----------
        data : FinalData
            data as returned by a Transformer
        """
        if len(data_list) == 1:
            self.plot_unique_period(data_list[0])
        else:
            self.plot_many_periods(data_list)

    def plot_many_periods(self, data_list):
        labels = []
        for i, data in enumerate(data_list):
            labels.append(data.report.final_label)
            for start, end, ppl in zip(data.x[::2], data.x[1::2], data.y[::2]):
                self.ax.plot([start, end], [i, i], c="k")
                self.ax.plot([start, start], [i - 0.1, i + 0.1], c="k")
                self.ax.plot([end, end], [i - 0.1, i + 0.1], c="k")
        self.ax.set_yticks(range(len(labels)))
        self.ax.set_yticklabels(labels)

    def plot_unique_period(self, data: FinalData):
        tr = self.ax.get_xaxis_transform()
        all_periods_s = []
        h = 0.7
        for start, end, ppl in zip(data.x[::2], data.x[1::2], data.y[::2]):
            s = fmt_period_short(start, end, ppl)
            all_periods_s.append((end, h, s))
            self._extra_info.append(fmt_period_long(start, end, ppl))
            (l,) = self.ax.plot(
                [start, end],
                [h, h],
                transform=tr,
                label=data.description,
                c="k",
            )
            self.ax.plot([start, start], [h - 0.05, h + 0.05], c="k", transform=tr)
            self.ax.plot([end, end], [h - 0.05, h + 0.05], c="k", transform=tr)

        if Config().plot.show_periods_info:
            for x, y, per in all_periods_s:
                self.period_info(per, x, y)
        self.legend_handles.append(l)
        self.legend_labels.append(_(data.description))

    def period_info(self, s: str, x: datetime.datetime, y: float = 0.7):
        self.ax.text(
            x,
            y - 0.05,
            s,
            transform=self.ax.get_xaxis_transform(),
            ha="right",
            va="top",
            bbox=dict(boxstyle="round", fc="w", ec="0.5", alpha=1),
            clip_on=False,
        )


def fmt_period_short(
    start: datetime.datetime, end: datetime.datetime, people: int
) -> str:
    num_days = (end - start).days + 1
    days = _("{days} d.").format(days=num_days)
    ppl = _("{ppl} p.").format(ppl=people)
    return f"{days} / {ppl}"


def fmt_period_long(
    start: datetime.datetime, end: datetime.datetime, people: int, wrap=False
) -> str:
    num_days = (end - start).days + 1
    days = ngettext("{} day", "{} days", num_days).format(num_days)
    ppl = ngettext("{} person", "{} people", people).format(people)
    return (
        f"{_(DATE_OUTPUT_FMT).format(dt=start)} - {_(DATE_OUTPUT_FMT).format(dt=end)}"
        + ("\n" if wrap else " ")
        + f"({days}, {ppl})"
    )
