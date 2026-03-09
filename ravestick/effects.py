import numpy as np


class BaseEffect:
    def process(self, frequency_bars):
        raise NotImplementedError("Subclasses must implement process()")


class ThreeBandCyanPulseEffect(BaseEffect):
    def __init__(self, leds_per_band):
        self.leds_per_band = leds_per_band

    def process(self, frequency_bars):
        bass = np.mean(frequency_bars[0:18])
        mids = np.mean(frequency_bars[18:54])
        highs = np.mean(frequency_bars[54:64])

        bands = [bass, mids, highs]
        led_colors = np.zeros((3, self.leds_per_band, 3), dtype=int)

        for band_idx, amplitude in enumerate(bands):
            # Amplitude is already 0.0 to 1.0, so just multiply by 255 for RGB intensity
            intensity = int(np.clip(amplitude * 255, 0, 255))
            color = (0, intensity, intensity)

            for led_idx in range(self.leds_per_band):
                led_colors[band_idx, led_idx] = color

        return led_colors


class ThreeBandVUMeterEffect(BaseEffect):
    def __init__(self, leds_per_band, bass_threshold=0.6):
        self.leds_per_band = leds_per_band
        self.bass_threshold = bass_threshold

        self.band_colors = [
            (255, 50, 50),  # Bass
            (50, 255, 50),  # Mids
            (50, 150, 255)  # Highs
        ]

    def process(self, frequency_bars):
        bass = np.mean(frequency_bars[0:18])
        mids = np.mean(frequency_bars[18:54])
        highs = np.mean(frequency_bars[54:64])

        bands = [bass, mids, highs]
        led_colors = np.zeros((3, self.leds_per_band, 3), dtype=int)

        for band_idx, amplitude in enumerate(bands):
            if band_idx == 0:
                # Trigger bass if it hits the threshold
                active_leds_count = self.leds_per_band if amplitude >= self.bass_threshold else 0
            else:
                # Amplitude is 0.0 to 1.0, so multiply by total LEDs to get how many to turn on
                active_leds_count = int(np.clip(amplitude * self.leds_per_band, 0, self.leds_per_band))

            for led_idx in range(active_leds_count):
                led_colors[band_idx, led_idx] = self.band_colors[band_idx]

        return led_colors


class EffectManager:
    def __init__(self, effects_list):
        self.effects = effects_list
        self.active_index = 0

    def next_effect(self):
        self.active_index = (self.active_index + 1) % len(self.effects)
        active_effect_name = self.effects[self.active_index].__class__.__name__
        print(f"Switched to visualizer: {active_effect_name}")

    def process(self, frequency_bars):
        return self.effects[self.active_index].process(frequency_bars)
