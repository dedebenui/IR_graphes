from collections import defaultdict
import datetime
from enum import Enum
import io
import itertools
from matplotlib import pyplot as plt
from emsapp.data import DataType, DataSet, FinalData


class PlotType(DataType):
    LINE = "line"
    BAR = "bar"
    PERIOD = "period"
    MIXED = "mixed"


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
        self.color_cycle = itertools.cycle(
            [
                "#1f77b4",
                "#ff7f0e",
                "#2ca02c",
                "#d62728",
                "#9467bd",
                "#8c564b",
                "#e377c2",
                "#7f7f7f",
                "#bcbd22",
                "#17becf",
            ]
        )
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
        if len(data_list)==1:
            data = data_list[0]
            for start, end in zip(data.x[::2], data.x[1::2]):
                self.ax.plot(
                    [start, end],
                    [0.5, 0.5],
                    transform=self.ax.get_xaxis_transform(),
                    label=data.description,
                    c="k",
                    marker="|",
                )
