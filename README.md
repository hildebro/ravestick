## Installation

### On x86
Run `uv sync`

### On arm
Install these packages:
`portaudio19-dev python3-all-dev libffi-dev`

Then run `uv venv` followed by `uv pip install --extra-index-url https://www.piwheels.org/simple -e .`
