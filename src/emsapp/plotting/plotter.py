from collections import defaultdict
import io
import itertools
from matplotlib import pyplot as plt
from emsapp.data import DataType, DataSet, FinalData


class Plotter:
    def __init__(self, ax: plt.Axes = None):
        self.indices: dict[DataType, int] = defaultdict(int)
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

    def as_bytes(self) -> bytes:
        with io.BytesIO() as buffer:
            self.fig.savefig(buffer, bbox_inches="tight", format="png", dpi=200)
            return buffer.getvalue()

    def plot(self, data_set: DataSet):
        for data in data_set:
            if data.data_type == DataType.LINE:
                self.plot_line(data)
            elif data.data_type == DataType.BAR:
                self.plot_bar(data)
            elif data.data_type == DataType.PERIOD:
                self.plot_period(data)
        self.ax.relim()
        self.ax.autoscale()

    def plot_line(self, data: FinalData):
        """plots a line

        Parameters
        ----------
        data : FinalData
            data as returned by a Transformer
        """
        self.ax.plot(data.x, data.y, label=data.description, color=next(self.color_cycle))

    def plot_bar(self, data: FinalData):
        """plots some bars

        Parameters
        ----------
        data : FinalData
            data as returned by a Transformer
        """
        self.ax.bar(data.x, data.y, label=data.description, color=next(self.color_cycle))

    def plot_period(self, data: FinalData):
        """plots some periods

        Parameters
        ----------
        data : FinalData
            data as returned by a Transformer
        """
        h = 0.5 + self.indices[DataType.PERIOD] / 25
        self.indices[DataType.PERIOD] += 1
        for start, end in zip(data.x[::2], data.x[1::2]):
            self.ax.plot(
                [start, end],
                [h, h],
                transform=self.ax.get_xaxis_transform(),
                label=data.description,
                c="k",
                marker="|",
            )
