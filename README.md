## Installation

### On x86
Run `uv run main.py` to build and start the project.

### On arm

#### Preconditions
Install these packages with the given package manager:  
`portaudio19-dev python3-all-dev libffi-dev libopenblas0`

#### Build
Run: `uv venv --python /usr/bin/python3 --system-site-packages`

Followed by:  
`uv pip install --extra-index-url https://www.piwheels.org/simple -e .`

#### Start

Run: `.venv/bin/python main.py`