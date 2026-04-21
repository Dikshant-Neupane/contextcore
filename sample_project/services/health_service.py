"""Health service: liveness and readiness probe helpers."""


def ping() -> str:
    """Return a simple liveness token confirming the process is alive."""
    return "pong"


def readiness_check(dependencies: dict[str, bool]) -> dict[str, object]:
    """Evaluate readiness based on a map of dependency-name to ok-flag.

    Returns a summary dict with overall status and individual results.
    """
    all_ok = all(dependencies.values())
    return {
        "status": "ready" if all_ok else "degraded",
        "checks": dependencies,
    }


def build_health_report(version: str, uptime_seconds: int) -> dict[str, object]:
    """Build a structured health report for external monitoring."""
    return {
        "version": version,
        "uptime_seconds": uptime_seconds,
        "status": "ok",
    }
