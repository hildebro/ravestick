import numpy as np


class BaseEffect:
    def process(self, frequency_bars):
        """Must return an array of RGB tuples: shape (BAR_COUNT, 3)"""
        raise NotImplementedError("Subclasses must implement process()")


class CyanPulseEffect(BaseEffect):
    def __init__(self, led_count):
        self.led_count = led_count

    def process(self, frequency_bars):
        """Converts frequency intensities into Cyan RGB values."""
        # scale to 0-255
        intensities = np.clip((frequency_bars / 5.0) * 255, 0, 255).astype(int)

        # Create an array of (R, G, B) colors
        colors = np.zeros((self.led_count, 3), dtype=int)

        # Set Green and Blue channels to the intensity to make Cyan
        colors[:, 1] = intensities  # Green
        colors[:, 2] = intensities  # Blue

        return colors


class ThreeBandVUMeterEffect:
    def __init__(self, leds_per_band, bass_threshold=2.5):
        self.leds_per_band = leds_per_band
        self.bass_threshold = bass_threshold
        # Distinct "ON" colors: Red for Bass, Green for Mids, Blue for Highs
        self.band_colors = [
            (255, 50, 50),  # Bass
            (50, 255, 50),  # Mids
            (50, 150, 255)  # Highs
        ]

    def process(self, frequency_bars):
        """Groups 64 bars into 3 bands. Bass is all-or-nothing, Mids/Highs are proportional."""
        # 1. Bucket the frequencies
        bass = np.mean(frequency_bars[0:10])  # Low frequencies
        mids = np.mean(frequency_bars[10:35])  # Mid frequencies
        highs = np.mean(frequency_bars[35:64])  # High frequencies

        bands = [bass, mids, highs]

        # Create an empty array for our LED colors. Shape: (3 bands, N leds, RGB)
        led_colors = np.zeros((3, self.leds_per_band, 3), dtype=int)

        for band_idx, amplitude in enumerate(bands):

            # --- BASS LOGIC: ALL OR NOTHING ---
            if band_idx == 0:
                if amplitude >= self.bass_threshold:
                    active_leds_count = self.leds_per_band
                else:
                    active_leds_count = 0

            # --- MIDS & HIGHS LOGIC: VU METER ---
            else:
                # Assuming an average max amplitude around 4.0; scale it to the number of LEDs
                active_leds_count = int(np.clip((amplitude / 4.0) * self.leds_per_band, 0, self.leds_per_band))

            # Turn ON the calculated number of LEDs from the bottom up
            for led_idx in range(active_leds_count):
                led_colors[band_idx, led_idx] = self.band_colors[band_idx]

        return led_colors
