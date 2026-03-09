import sys
import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtWidgets


class BaseDisplay:
    def update(self, frequency_bars, led_colors):
        raise NotImplementedError

    def is_active(self):
        raise NotImplementedError


class GUIDisplay(BaseDisplay):
    def __init__(self, bar_count):
        self.bar_count = bar_count

        # Set up the GUI
        self.app = QtWidgets.QApplication(sys.argv)
        self.win = pg.GraphicsLayoutWidget(show=True, title="Ravestick Live Spectrum")
        self.plot = self.win.addPlot(title="Frequency Bars")

        self.x = np.arange(self.bar_count)

        # frequency bars
        self.bargraph = pg.BarGraphItem(x=self.x, height=np.zeros(bar_count), width=0.8, brush='c')
        self.plot.addItem(self.bargraph)

        # virtual LED strip
        self.led_y_positions = np.full(self.bar_count, 5.5)
        self.led_brushes = [pg.mkBrush(color=(0, 0, 0)) for _ in range(self.bar_count)]
        self.led_strip = pg.ScatterPlotItem(
            x=self.x,
            y=self.led_y_positions,
            size=15,
            symbol='o',
            brush=self.led_brushes,
            pen=pg.mkPen(color=(50, 50, 50))
        )
        self.plot.addItem(self.led_strip)

        self.plot.setYRange(0, 6)
        self.plot.setXRange(0, self.bar_count)
        self.plot.hideAxis('bottom')

    def update(self, frequency_bars, led_colors):
        """Updates the GUI with the latest bars and colors."""
        # Update bars
        self.bargraph.setOpts(height=frequency_bars)

        # Update virtual LEDs
        for i in range(self.bar_count):
            self.led_brushes[i] = pg.mkBrush(color=tuple(led_colors[i]))

        self.led_strip.setData(x=self.x, y=self.led_y_positions, brush=self.led_brushes)

        # redraw
        self.app.processEvents()

    def is_active(self):
        """Returns True as long as the window is open."""
        return self.win.isVisible()
