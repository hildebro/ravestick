import numpy as np


class AudioAnalyzer:
    def __init__(self, bar_count, decay_ratio):
        self.bar_count = bar_count
        self.decay_ratio = decay_ratio

        # We have 129 actual FFT bins (from a 256 blocksize).
        self.x_fft = np.arange(129)

        # We define the exact fractional points we want to sample,
        # stretching smoothly from bin 1 (62.5 Hz) to bin 128 (8000 Hz).
        self.x_bars = np.logspace(0, np.log10(128), num=self.bar_count)

        self.current_bars = np.zeros(self.bar_count)

    def process(self, raw_audio_data):
        """Takes raw audio chunk, performs FFT, interpolates, and applies decay."""
        data = raw_audio_data.squeeze(axis=1)

        # 1. Get the raw FFT data
        fft_data = np.abs(np.fft.rfft(data))

        # 2. INTERPOLATE! This draws a smooth line between the sparse low-end bins,
        # completely eliminating the "duplicate bar" problem.
        smoothed_fft = np.interp(self.x_bars, self.x_fft, fft_data)

        # 3. Apply the decay drop-off
        self.current_bars = np.maximum(smoothed_fft, self.current_bars * self.decay_ratio)

        return self.current_bars
