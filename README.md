# Ravestick

Listens to music around you and turns it into light patterns.

These instructions are written specifically to get the software running on a BeagleBone Black with an INMP441
microphone. I've written it down mostly as a future reference for myself. If you found this repository and want to try
it out yourself with different hardware, you will have to make adjustments.

## Hardware setup

Connect the pins:

| INMP441 Pin	 | BeagleBone Black Pin | Function / Description                                                                                                                 |
|:-------------|----------------------|----------------------------------------------------------------------------------------------------------------------------------------|
| VDD	         | P9_03	               | 3.3V Power. (Do not use 5V, as it will damage the mic and the BBB's data pins).                                                        |
| GND	         | P9_01	               | Ground.                                                                                                                                |
| L/R	         | P9_02	               | Channel Select. Connecting this to Ground (P9_02) sets the mic to output on the Left channel, which is standard for a single mono mic. |
| SCK	         | P9_31	               | Serial Clock / Bit Clock (mcasp0_aclkx). Provides the timing for the data bits.                                                        |
| WS	          | P9_29	               | Word Select / Frame Sync (mcasp0_fsx). Tells the system if the data is for the left or right channel.                                  |
| SD	          | P9_30	               | Serial Data In (mcasp0_axr0). This is where the actual audio data is sent into the BBB.                                                |

## Software setup

### Packages

Install these packages with the given package manager:  
`portaudio19-dev python3-all-dev libffi-dev libopenblas0`

### Device tree overlay

You need to tell the BeagleBone what to do with those connected pins from above. Compile the definitions via:  
`dtc -O dtb -o BB-INMP441-00A0.dtbo -b 0 -@ BB-INMP441-00A0.dts`
Then move the generated `dtbo` file to `/lib/firmware/`.  

Finally, that `dtbo` file must be loaded. Modify `/boot/uEnv.txt` in the section `###Additional custom capes` add:  
`uboot_overlay_addr4=/lib/firmware/BB-INMP441-00A0.dtbo`

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

Make sure to install `alsa-utils` on the arm chip.

Use `arecord -l` to see, if your microphone is recognized.