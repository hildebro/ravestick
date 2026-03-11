import sounddevice as sd

from ravestick.audio import AudioAnalyzer
from ravestick.config import BAR_COUNT, BAR_DECAY_RATIO, LEDS_PER_BAND
from ravestick.displays import WebDisplay
from ravestick.effects import EffectManager, ThreeBandVUMeterEffect, ThreeBandCyanPulseEffect


def main():
    analyzer = AudioAnalyzer(BAR_COUNT, BAR_DECAY_RATIO)

    effect_vu = ThreeBandVUMeterEffect(LEDS_PER_BAND)
    effect_pulse = ThreeBandCyanPulseEffect(LEDS_PER_BAND)

    manager = EffectManager([effect_vu, effect_pulse])

    display = WebDisplay(port=5000, on_switch_callback=manager.next_effect)

    # Ask ALSA for the default input device info
    try:
        default_mic = sd.query_devices(kind='input')
        print(f"Using Mic: {default_mic['name']}")
    except ValueError:
        print("No default ALSA input device found! You may need to specify a device ID.")
        return

    # main processing loop
    try:
        # sd.InputStream streams raw audio data into numpy arrays.
        # channels=1 ensures a flat, predictable mono array for your analyzer.
        with sd.InputStream(samplerate=16000, blocksize=256, channels=1) as stream:

            while display.is_active():
                # stream.read() returns the numpy array AND a boolean overflow flag
                raw_data, overflow = stream.read(256)

                if overflow:
                    # Useful for tuning: if this prints, the BeagleBone is taking
                    # too long to crunch the math and dropped some audio frames.
                    print("Warning: Audio buffer overflow!")

                freq_bars = analyzer.process(raw_data)
                led_colors = manager.process(freq_bars)
                display.update(freq_bars, led_colors)

    except KeyboardInterrupt:
        print("\nShutting down gracefully...")
        display.active = False

    except sd.PortAudioError as e:
        print(f"\nALSA Audio Error: {e}")
        print("Run 'python -m sounddevice' in your terminal to list actual device IDs.")


if __name__ == "__main__":
    main()
