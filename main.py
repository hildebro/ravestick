import sys

import numpy as np
import pyqtgraph as pg
import soundcard as sc
from pyqtgraph.Qt import QtWidgets


def main():
    print("Hello from ravestick!")

    # 1. Setup the GUI (No QTimer needed this time)
    app = QtWidgets.QApplication(sys.argv)
    win = pg.GraphicsLayoutWidget(show=True, title="Ravestick Live Spectrum")
    plot = win.addPlot(title="Frequency Bars")

    num_bars = 129
    x = np.arange(num_bars)
    y = np.zeros(num_bars)

    bargraph = pg.BarGraphItem(x=x, height=y, width=0.8, brush='c')
    plot.addItem(bargraph)

    plot.setYRange(0, 5) # Adjust based on mic sensitivity
    plot.setXRange(0, 129)
    plot.hideAxis('bottom')

    # 2. Setup Audio
    default_speaker = sc.default_speaker()
    default_mic = sc.default_microphone()

    print(f"Using Mic: {default_mic.name}")

    # 3. The Synchronous Loop
    with default_mic.recorder(samplerate=16000, blocksize=256) as mic, \
            default_speaker.player(samplerate=16000, blocksize=256) as sp:

        # Run as long as the graphical window remains open
        while win.isVisible():
            # Capture and play audio
            data = mic.record(numframes=256)
            sp.play(data)

            # We have array of arrays of a single number, so we squeeze one layer.
            data = data.squeeze(axis=1)
            fft_data = np.abs(np.fft.rfft(data))

            # Math: Apply visual decay for smooth falling bars
            # Note for later: would be nice to not have any decay, but then we might get timing issues. Try it out later.
            y = np.maximum(fft_data, y * 0.5)

            # Update the graph data
            bargraph.setOpts(height=y)

            # THE MAGIC TRICK: Force the GUI to redraw right now
            app.processEvents()

if __name__ == "__main__":
    main()