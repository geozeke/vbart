"""Package-level constants used by vbart."""

from pathlib import Path

PASS = "✅"
FAIL = "❌"

APP_NAME = "vbart"
ARG_PARSERS_BASE = Path(__file__).parent / "parsers"
BASE_IMAGE = "alpine:3.23"
HELPER_IMAGE_VERSION = "2"
HELPER_IMAGE_VERSION_LABEL = "org.opencontainers.image.vbart.helper-version"
UTILITY_IMAGE = "vbart_utility"
