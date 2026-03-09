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
