"""Application entry point."""

from sample_project.core.app import app_name, app_version, build_banner
from sample_project.core.config import get_config, is_production


def run() -> int:
    """Bootstrap the application and return an exit code.

    Reads config, prints the startup banner, and confirms the environment.
    Returns 0 on success.
    """
    config = get_config()
    banner = build_banner(config.get("env", "dev"))
    print(banner)
    if is_production(config):
        print("WARNING: running in production mode")
    print(f"version={app_version()} app={app_name()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
