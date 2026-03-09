import sys

import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtWidgets


class GUIDisplay:
    def __init__(self, bar_count, leds_per_band):
        self.bar_count = bar_count
        self.leds_per_band = leds_per_band

        # Setup GUI
        self.app = QtWidgets.QApplication(sys.argv)
        self.win = pg.GraphicsLayoutWidget(show=True, title="Ravestick Live Spectrum")
        self.plot = self.win.addPlot(title="3-Band VU Meter")

        # Background Frequency Bars
        self.x = np.arange(self.bar_count)
        self.bargraph = pg.BarGraphItem(x=self.x, height=np.zeros(bar_count), width=0.8, brush=(50, 50, 50, 150))
        self.plot.addItem(self.bargraph)

        # --- THE VIRTUAL VERTICAL LED STRIPS ---
        # Center the 3 strips over the 0-63 X-axis: Bass (~x=5), Mids (~x=32), Highs (~x=55)
        self.band_x_positions = [5, 32, 55]

        self.led_x = []
        self.led_y = []

        # Create coordinates for all LEDs
        for x in self.band_x_positions:
            for y in range(self.leds_per_band):
                self.led_x.append(x)
                # Space them vertically so they fit within the 0 to 6 Y-axis bounds
                self.led_y.append((y * 0.25) + 0.5)

        self.total_leds = 3 * self.leds_per_band
        self.led_brushes = [pg.mkBrush(color=(0, 0, 0)) for _ in range(self.total_leds)]

        self.led_strip = pg.ScatterPlotItem(
            x=self.led_x,
            y=self.led_y,
            size=20,  # Made them slightly larger for visibility
            symbol='s',  # 's' makes them square, like real LED strips
            brush=self.led_brushes,
            pen=pg.mkPen(color=(30, 30, 30))
        )
        self.plot.addItem(self.led_strip)

        self.plot.setYRange(0, 6)
        self.plot.setXRange(0, self.bar_count)
        self.plot.hideAxis('bottom')

    def update(self, frequency_bars, led_colors):
        # Update background bars
        self.bargraph.setOpts(height=frequency_bars)

        # Update Vertical LEDs
        flat_idx = 0
        for band_idx in range(3):
            for led_idx in range(self.leds_per_band):
                self.led_brushes[flat_idx] = pg.mkBrush(color=tuple(led_colors[band_idx, led_idx]))
                flat_idx += 1

        self.led_strip.setData(x=self.led_x, y=self.led_y, brush=self.led_brushes)
        self.app.processEvents()

    def is_active(self):
        return self.win.isVisible()
