import numpy as np


class AudioAnalyzer:
    def __init__(self, bar_count, decay_ratio):
        self.bar_count = bar_count
        self.decay_ratio = decay_ratio
        self.log_indices = np.logspace(0, np.log10(self.bar_count * 2), num=self.bar_count).astype(int)
        self.current_bars = np.zeros(self.bar_count)

    def process(self, raw_audio_data):
        """Takes raw audio chunk, performs FFT, and applies decay."""
        data = raw_audio_data.squeeze(axis=1)

        fft_data = np.abs(np.fft.rfft(data))
        fft_data = fft_data[self.log_indices]

        self.current_bars = np.maximum(fft_data, self.current_bars * self.decay_ratio)

        return self.current_bars
