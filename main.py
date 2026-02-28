import soundcard as sc
import numpy as np

def main():
    print("Hello from ravestick!")
    # get a list of all speakers:
    speakers = sc.all_speakers()
    # get the current default speaker on your system:
    default_speaker = sc.default_speaker()
    # get a list of all microphones:
    mics = sc.all_microphones()
    # get the current default microphone on your system:
    default_mic = sc.default_microphone()
    print(mics)
    print(default_mic)

    # alternatively, get a `Recorder` and `Player` object
    # and play or record continuously:
    with default_mic.recorder(samplerate=48000, blocksize=256) as mic, \
          default_speaker.player(samplerate=48000, blocksize=256) as sp:
        for _ in range(5000):
            data = mic.record(numframes=256)
            sp.play(data)


if __name__ == "__main__":
    main()
