import sys
import threading

import numpy as np
import pyqtgraph as pg
import soundcard as sc
from pyqtgraph.Qt import QtCore, QtWidgets

# Shared array to pass data between the audio thread and the GUI thread.
# np.fft.rfft on 256 frames gives 129 frequency bins.
latest_fft_data = np.zeros(129)

def audio_loop():
    """This runs in the background, handling mic input and speaker output."""
    global latest_fft_data
    print("Hello from ravestick audio thread!")

    default_speaker = sc.default_speaker()
    default_mic = sc.default_microphone()

    with default_mic.recorder(samplerate=48000, blocksize=256) as mic, \
            default_speaker.player(samplerate=48000, blocksize=256) as sp:

        # Changed from range(5000) to True so it runs as long as the window is open
        while True:
            data = mic.record(numframes=256)
            sp.play(data)

            # --- PROCESS FOR VISUALIZATION ---
            # 1. Soundcard returns (frames, channels). Average them to get mono audio.
            mono_data = data.mean(axis=1)

            # 2. Compute the FFT to get frequency amplitudes (bass to treble)
            fft_data = np.abs(np.fft.rfft(mono_data))

            # 3. Update the shared variable for the GUI to read
            latest_fft_data = fft_data

class LiveBarChart:
    def __init__(self):
        self.app = QtWidgets.QApplication(sys.argv)
        self.win = pg.GraphicsLayoutWidget(show=True, title="Ravestick Live Spectrum")
        self.plot = self.win.addPlot(title="Frequency Bars")

        self.num_bars = 129
        self.x = np.arange(self.num_bars)
        self.y = np.zeros(self.num_bars)

        # Create the visual bars
        self.bargraph = pg.BarGraphItem(x=self.x, height=self.y, width=0.8, brush='c')
        self.plot.addItem(self.bargraph)

        # Set fixed axes so the bars don't jump around
        self.plot.setYRange(0, 5) # Adjust this max value if the bars are too tall/short
        self.plot.setXRange(0, 129)
        self.plot.hideAxis('bottom') # Hiding X axis for a cleaner look

        # GUI Timer pulls data 30 times a second
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(33)

    def update(self):
        global latest_fft_data

        # Apply visual decay so the bars fall smoothly instead of flickering
        # new_height = max(current_audio, previous_height * 0.8)
        self.y = np.maximum(latest_fft_data * 1.5, self.y * 0.8)

        self.bargraph.setOpts(height=self.y)

    def run(self):
        if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
            sys.exit(self.app.exec())

if __name__ == "__main__":
    # 1. Start the audio loop in a "daemon" thread (closes automatically when main thread dies)
    audio_thread = threading.Thread(target=audio_loop, daemon=True)
    audio_thread.start()

    # 2. Start the GUI event loop in the main thread
    viz = LiveBarChart()
    viz.run()