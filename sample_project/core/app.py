"""Core application bootstrap helpers."""

APP_NAME = "sample-project"
APP_VERSION = "0.1.0"


def app_name() -> str:
    """Return the canonical application name string."""
    return APP_NAME


def app_version() -> str:
    """Return the current semantic version string."""
    return APP_VERSION


def build_banner(env: str) -> str:
    """Build a startup banner string for log output."""
    return f"{APP_NAME} v{APP_VERSION} [{env.upper()}]"
