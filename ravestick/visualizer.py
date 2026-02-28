import numpy as np

from ravestick.config import BAR_COUNT


class Visualizer:
    values = np.zeros(BAR_COUNT)

    def update(self, numpy_array):
        intensities = np.clip((numpy_array / 5.0) * 255, 0, 255).astype(int)

        self.values = intensities
        # Create new colors for each LED based on the intensity
        #for i in range(BAR_COUNT):
            # (R, G, B) - pulsing Cyan just like before
            # color = (0, intensities[i], intensities[i])
            #self.values[i] = intensities[i]

    def output(self):
        return self.values