from datetime import datetime, timezone

def utcnow_aware():
    """Devuelve la hora actual en UTC como datetime aware."""
    return datetime.now(timezone.utc)
