import numpy as np

from ravestick.config import SENSITIVITY


class AudioAnalyzer:
    def __init__(self, bar_count, decay_ratio, max_db=60.0):
        self.bar_count = bar_count
        self.decay_ratio = decay_ratio
        self.max_db = max_db

        self.x_fft = np.arange(129)
        self.x_bars = np.logspace(0, np.log10(128), num=self.bar_count)
        self.current_bars = np.zeros(self.bar_count)

        # A subtle visual boost for the highs to make the visualizer look flat and even.
        # Scales from 1.0x at the bass to 4.0x at the extreme highs.
        self.weighting = np.linspace(1.0, 4, self.bar_count)

    def process(self, raw_audio_data):
        data = raw_audio_data.squeeze(axis=1)

        # Apply fft and interpolation
        processed_data = np.abs(np.fft.rfft(data))
        processed_data = np.interp(self.x_bars, self.x_fft, processed_data)

        # Convert to Decibels
        processed_data = 20 * np.log10(processed_data + 1)

        # Apply the visual weighting
        processed_data = processed_data * self.weighting

        # Apply decay
        processed_data = np.maximum(processed_data, self.current_bars * self.decay_ratio)

        # Normalize into a window of 0.0 to 1.0
        processed_data = np.clip(processed_data / self.max_db, 0.0, 1.0)

        # Boost by sensitivity value
        processed_data = np.clip(processed_data * SENSITIVITY, 0.0, 1.0)

        self.current_bars = processed_data

        return self.current_bars
