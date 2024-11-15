"""Constants."""

from pathlib import Path

GREEN = "\033[0;32;49m"
RED = "\033[0;31;49m"
COLOR_END = "\x1b[0m"

PASS = f"{GREEN}\u2714{COLOR_END}"
FAIL = f"{RED}\u2718{COLOR_END}"

HOME = Path(__file__).parent

APP_NAME = "vbart"
ARG_PARSERS_BASE = HOME / "parsers"
BASE_IMAGE = "alpine:latest"
DOCKERFILE_PATH = HOME
UTILITY_IMAGE = "vbart_utility"
VERSION = "0.1.5"
