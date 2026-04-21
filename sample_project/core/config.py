"""Core configuration loader."""

DEFAULT_CONFIG: dict[str, str] = {
    "env": "dev",
    "region": "local",
    "log_level": "INFO",
    "timeout": "30",
}


def get_config() -> dict[str, str]:
    """Return the default application configuration map."""
    return dict(DEFAULT_CONFIG)


def get_value(key: str, fallback: str = "") -> str:
    """Retrieve a single config value by key with an optional fallback."""
    return DEFAULT_CONFIG.get(key, fallback)


def is_production(config: dict[str, str]) -> bool:
    """Return True if the config environment is set to production."""
    return config.get("env", "").lower() == "prod"
