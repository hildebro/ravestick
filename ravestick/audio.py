import numpy as np


class AudioAnalyzer:
    def __init__(self, bar_count, decay_ratio, max_db=60.0):
        self.bar_count = bar_count
        self.decay_ratio = decay_ratio
        self.max_db = max_db

        self.x_fft = np.arange(129)
        self.x_bars = np.logspace(0, np.log10(128), num=self.bar_count)
        self.current_bars = np.zeros(self.bar_count)

        # A subtle visual boost for the highs to make the visualizer look flat and even.
        # Scales from 1.0x at the bass to 2.5x at the extreme highs.
        self.weighting = np.linspace(1.0, 4, self.bar_count)

    def process(self, raw_audio_data):
        data = raw_audio_data.squeeze(axis=1)

        fft_data = np.abs(np.fft.rfft(data))
        smoothed_fft = np.interp(self.x_bars, self.x_fft, fft_data)

        # 1. Convert to Decibels
        db_fft = 20 * np.log10(smoothed_fft + 1)

        # 2. Apply the visual weighting
        weighted_db = db_fft * self.weighting

        # 3. NORMALIZE to 0.0 -> 1.0 so it never breaks the web UI
        normalized_bars = np.clip(weighted_db / self.max_db, 0.0, 1.0)

        # 4. Apply decay
        self.current_bars = np.maximum(normalized_bars, self.current_bars * self.decay_ratio)

        return self.current_bars
