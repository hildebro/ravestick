import sys

import numpy as np
import pyqtgraph as pg
import soundcard as sc
from pyqtgraph.Qt import QtWidgets

from ravestick.config import BAR_COUNT, BAR_DECAY_RATIO
from ravestick.visualizer import Visualizer


def main():
    print("Hello from ravestick!")

    visualizer = Visualizer()

    # 1. Setup the GUI
    app = QtWidgets.QApplication(sys.argv)
    win = pg.GraphicsLayoutWidget(show=True, title="Ravestick Live Spectrum")
    plot = win.addPlot(title="Frequency Bars")

    x = np.arange(BAR_COUNT)
    y = np.zeros(BAR_COUNT)

    # The frequency bars
    bargraph = pg.BarGraphItem(x=x, height=y, width=0.8, brush='c')
    plot.addItem(bargraph)

    # --- THE VIRTUAL LED STRIP ---
    # We create a row of dots at y=5.5 (just above the bar graph's max height)
    led_y_positions = np.full(BAR_COUNT, 5.5)
    # Default brushes (black/off)
    led_brushes = [pg.mkBrush(color=(0, 0, 0)) for _ in range(BAR_COUNT)]

    led_strip = pg.ScatterPlotItem(
        x=x,
        y=led_y_positions,
        size=15,
        symbol='o',
        brush=led_brushes,
        pen=pg.mkPen(color=(50, 50, 50))  # Subtle border around the "LEDs"
    )
    plot.addItem(led_strip)

    log_indices = np.logspace(0, np.log10(BAR_COUNT * 2), num=BAR_COUNT).astype(int)

    # Increased Y-range slightly to fit our new virtual LED strip
    plot.setYRange(0, 6)
    plot.setXRange(0, BAR_COUNT)
    plot.hideAxis('bottom')

    # 2. Setup Audio
    default_speaker = sc.default_speaker()
    default_mic = sc.default_microphone()

    print(f"Using Mic: {default_mic.name}")

    # 3. The Synchronous Loop
    with default_mic.recorder(samplerate=16000, blocksize=256) as mic, \
            default_speaker.player(samplerate=16000, blocksize=256) as sp:

        while win.isVisible():
            data = mic.record(numframes=256)
            data = data.squeeze(axis=1)
            fft_data = np.abs(np.fft.rfft(data))
            fft_data = fft_data[log_indices]

            # Math: Apply visual decay
            y = np.maximum(fft_data, y * BAR_DECAY_RATIO)
            bargraph.setOpts(height=y)

            # --- UPDATE VIRTUAL LEDS ---
            visualizer.update(y)

            # Create new colors for each LED based on the intensity
            for i in range(BAR_COUNT):
                # (R, G, B) - pulsing Cyan just like before
                color = (0, visualizer.output()[i], visualizer.output()[i])
                led_brushes[i] = pg.mkBrush(color=color)

            # Push the updated colors to the scatter plot
            led_strip.setData(x=x, y=led_y_positions, brush=led_brushes)

            # Force the GUI to redraw right now
            app.processEvents()


if __name__ == "__main__":
    main()
