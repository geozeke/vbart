"""Constants."""

from pathlib import Path

PASS = "✅"
FAIL = "❌"

HOME = Path(__file__).parent

APP_NAME = "vbart"
ARG_PARSERS_BASE = HOME / "parsers"
BASE_IMAGE = "alpine:latest"
DOCKERFILE_PATH = HOME
UTILITY_IMAGE = "vbart_utility"
