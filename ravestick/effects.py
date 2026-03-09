import numpy as np


class BaseEffect:
    def process(self, frequency_bars):
        """Must return an array of RGB tuples: shape (BAR_COUNT, 3)"""
        raise NotImplementedError("Subclasses must implement process()")


class ThreeBandCyanPulseEffect:
    def __init__(self, leds_per_band):
        self.leds_per_band = leds_per_band

    def process(self, frequency_bars):
        """Groups 64 bars into 3 bands. Pulses the entire vertical strip in Cyan based on intensity."""
        # Bass: 62.5 Hz to ~250 Hz (The Kick & Sub)
        bass = np.mean(frequency_bars[0:18])
        # Mids: ~250 Hz to ~4,000 Hz (Vocals, Snare, Synths, Guitars)
        mids = np.mean(frequency_bars[18:54])
        # Highs: ~4,000 Hz to 8,000 Hz (Cymbals, Hi-hats, Air)
        highs = np.mean(frequency_bars[54:64])

        bands = [bass, mids, highs]

        # Create an empty array for our LED colors. Shape: (3 bands, N leds, RGB)
        led_colors = np.zeros((3, self.leds_per_band, 3), dtype=int)

        for band_idx, amplitude in enumerate(bands):
            # Scale amplitude to a 0-255 brightness value (assuming average max amplitude is ~5.0)
            intensity = int(np.clip((amplitude / 5.0) * 255, 0, 255))

            # Pulse Cyan (R=0, G=intensity, B=intensity)
            color = (0, intensity, intensity)

            # Apply this exact color to EVERY LED in the current vertical band
            for led_idx in range(self.leds_per_band):
                led_colors[band_idx, led_idx] = color

        return led_colors


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
        # Bass: 62.5 Hz to ~250 Hz (The Kick & Sub)
        bass = np.mean(frequency_bars[0:18])
        # Mids: ~250 Hz to ~4,000 Hz (Vocals, Snare, Synths, Guitars)
        mids = np.mean(frequency_bars[18:54])
        # Highs: ~4,000 Hz to 8,000 Hz (Cymbals, Hi-hats, Air)
        highs = np.mean(frequency_bars[54:64])

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


class EffectManager:
    def __init__(self, effects_list):
        self.effects = effects_list
        self.active_index = 0

    def next_effect(self):
        """Cycles to the next visualizer in the list."""
        self.active_index = (self.active_index + 1) % len(self.effects)
        active_effect_name = self.effects[self.active_index].__class__.__name__
        print(f"Switched to visualizer: {active_effect_name}")

    def process(self, frequency_bars):
        """Passes the audio data to the currently active visualizer."""
        return self.effects[self.active_index].process(frequency_bars)
