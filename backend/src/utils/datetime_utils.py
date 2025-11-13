from datetime import UTC, datetime


def utcnow_aware():
    """Devuelve la hora actual en UTC como datetime aware."""
    return datetime.now(UTC)
