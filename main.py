import soundcard as sc

from ravestick.audio import AudioAnalyzer
from ravestick.config import BAR_COUNT, BAR_DECAY_RATIO, LEDS_PER_BAND
from ravestick.displays import WebDisplay
from ravestick.effects import EffectManager, ThreeBandVUMeterEffect, ThreeBandCyanPulseEffect


def main():
    print("Hello from ravestick!")

    analyzer = AudioAnalyzer(BAR_COUNT, BAR_DECAY_RATIO)

    effect_vu = ThreeBandVUMeterEffect(LEDS_PER_BAND)
    effect_cyan = ThreeBandCyanPulseEffect(LEDS_PER_BAND)

    manager = EffectManager([effect_vu, effect_cyan])

    display = WebDisplay(port=5000, on_switch_callback=manager.next_effect)

    default_mic = sc.default_microphone()
    print(f"Using Mic: {default_mic.name}")

    # main processing loop
    try:
        with default_mic.recorder(samplerate=16000, blocksize=256) as mic:
            while display.is_active():
                raw_data = mic.record(numframes=256)

                freq_bars = analyzer.process(raw_data)

                led_colors = manager.process(freq_bars)

                display.update(freq_bars, led_colors)
    except KeyboardInterrupt:
        print("\nShutting down gracefully...")
        display.active = False


if __name__ == "__main__":
    main()
