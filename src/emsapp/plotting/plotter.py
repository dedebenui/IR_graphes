import datetime
import io
import itertools
from collections import defaultdict
from enum import Enum
from typing import Optional

import matplotlib.dates as mdates
import numpy as np
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
    lims: Optional[tuple[datetime.date, datetime.date]]
    _extra_info: list[str]
    _sec_ax = None
    _ymax = None

    def __init__(self, data_set: DataSet, ax: plt.Axes = None):
        self.indices: dict[DataType, int] = defaultdict(int)
        self.legend_handles = []
        self.legend_labels = []
        self._extra_info = []
        self.update_lims()
        if ax:
            self.ax = ax
            self.fig = self.ax.get_figure()
        else:
            self.fig, self.ax = plt.subplots(figsize=Config().plot.figsize)
        self.title = data_set.title
        self.data = defaultdict(list)
        tpe = self.plot_type = PlotType.MIXED
        for data in data_set:
            self.data[data.data_type].append(data)
            tpe = data.data_type.value
        if len(self.data) == 1:
            self.plot_type = PlotType(tpe)
        self.update_styles()
        self.plot()

    def update_styles(self):
        if self.plot_type is PlotType.MIXED:
            n = len(COLORS[::2])
            self.line_colors = itertools.cycle(COLORS[::2])
            self.bar_colors = itertools.cycle(COLORS[1::2])
        else:
            n = len(COLORS)
            self.line_colors = itertools.cycle(COLORS)
            self.bar_colors = itertools.cycle(COLORS)
        self.line_styles = itertools.cycle(["-"] * n + ["--"] * n)

    def update_lims(self):
        if Config().plot.show_everything:
            self.lims = None
            return
        self.lims = (Config().plot.date_start, Config().plot.date_end)

    def update_ymax(self, xs, ys):
        if self.lims and len(xs) > 0:
            self._ymax = max(
                self._ymax or 1,
                max(
                    [y for x, y in zip(xs, ys) if self.lims[0] <= x <= self.lims[1]]
                    or [1]
                ),
            )

    @property
    def extra_info(self) -> str:
        return "\n".join(self._extra_info)

    def as_bytes(self) -> bytes:
        with io.BytesIO() as buffer:
            self.fig.savefig(buffer, bbox_inches="tight", format="png", dpi=200)
            return buffer.getvalue()

    def plot(self):
        self.update_lims()
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
            self.ax.axvline(datetime.date.today(), c="r", lw=2)
        self.ax.relim()
        self.ax.autoscale()
        if self.lims:
            l, r = self.lims
            hd = datetime.timedelta(0.5)
            self.ax.set_xlim(
                datetime.datetime(l.year, l.month, l.day) - hd,
                datetime.datetime(r.year, r.month, r.day) + hd,
            )
            if self._ymax:
                self.ax.set_ylim(0, self._ymax + 0.5)
        self.fmt_xaxis()

    def legend(self, loc: LegendLoc):
        if not self.legend_handles:
            return
        if loc == LegendLoc.ABOVE:
            self.ax.legend(
                self.legend_handles,
                self.legend_labels,
                bbox_to_anchor=(0, 1.02, 1, 0.6),
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
        if duration > 365:
            self.ax.xaxis.set_major_locator(mdates.MonthLocator(bymonthday=(1,)))
            self.ax.xaxis.set_major_formatter(formatter)
        elif duration > 180:
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
            self.update_ymax(data.x, data.y)
            (l,) = self.ax.plot(
                data.x, data.y, color=next(self.line_colors), ls=next(self.line_styles)
            )
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
            self.update_ymax(data.x, data.y)
            x = np.array([datetime.datetime(d.year, d.month, d.day) for d in data.x])
            cont = self.ax.bar(
                x + start + i * offset,
                data.y,
                offset,
                color=next(self.bar_colors),
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
        line = None
        for start, end, ppl in zip(data.x[::2], data.x[1::2], data.y[::2]):
            if self.lims and (start > self.lims[1] or end < self.lims[0]):
                continue
            s = fmt_period_short(start, end, ppl)
            all_periods_s.append((end, h, s))
            self._extra_info.append(fmt_period_long(start, end, ppl))
            (line,) = self.ax.plot(
                [start, end],
                [h, h],
                transform=tr,
                label=data.description,
                c="k",
            )
            self.ax.plot([start, start], [h - 0.02, h + 0.02], c="k", transform=tr)
            self.ax.plot([end, end], [h - 0.02, h + 0.02], c="k", transform=tr)

        if Config().plot.show_periods_info:
            for x, y, per in all_periods_s:
                self.period_info(per, x, y)
        if line:
            self.legend_handles.append(line)
            self.legend_labels.append(_(data.description))

    def period_info(self, s: str, x: datetime.date, y: float = 0.7):
        if self.lims:
            x = max(min(self.lims[1], x), self.lims[0])
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


def fmt_period_short(start: datetime.date, end: datetime.date, people: int) -> str:
    num_days = (end - start).days + 1
    days = _("{days} d.").format(days=num_days)
    ppl = _("{ppl} p.").format(ppl=people)
    return f"{days} / {ppl}"


def fmt_period_long(
    start: datetime.date, end: datetime.date, people: int, wrap=False
) -> str:
    num_days = (end - start).days + 1
    days = ngettext("{} day", "{} days", num_days).format(num_days)
    ppl = ngettext("{} person", "{} people", people).format(people)
    return (
        f"{_(DATE_OUTPUT_FMT).format(dt=start)} - {_(DATE_OUTPUT_FMT).format(dt=end)}"
        + ("\n" if wrap else " ")
        + f"({days}, {ppl})"
    )
