# Ravestick

Listens to music around you and turns it into light patterns.

These instructions are written specifically to get the software running on a BeagleBone Black. I've written it down
mostly as a future reference for myself. If you found this repository and want to try it out yourself with different
hardware, you will have to make adjustments.

## Hardware setup

You will need:

- BeagleBone Black
    - If you use another SoC, make sure that it has an analog-to-digital converter. Otherwise, the potentiometers won't
      work.
- USB microphone
    - I've tried using an I2S microphone. But it's a pain to set up with the BeagleBone. The microphone didn't show up
      at all until I disabled the HDMI functionality. Sadly, I2S microphones require an external heartbeat and the
      BeagleBone has its heartbeat linked to the HDMI output. So it seems an external crystal oscillator is required to
      make this work and at that point, I just defaulted back to a simple USB microphone.

## Software setup

### Packages

Install these packages with the given package manager:  
`portaudio19-dev python3-all-dev libffi-dev libopenblas0`

### Build

Note that we can't simply run `uv sync`, because it would try to compile numpy. That will take hours on a weak SoC.

Run: `uv venv --python /usr/bin/python3 --system-site-packages`

Followed by:  
`uv pip install --extra-index-url https://www.piwheels.org/simple -e .`

### Start

Note that `uv run main.py` won't work, because it will not recognize the existing build.

Run: `.venv/bin/python main.py`

## Development

### Demo on x86

Run `uv run main.py` to build and start the project.

### Debug on arm

Use `arecord -l` (comes with package `alsa-utils`) to see, if your microphone is recognized.