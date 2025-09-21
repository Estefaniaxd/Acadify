from datetime import datetime, timezone


def utcnow_aware() -> datetime:
    """Obtener fecha y hora actual en UTC con timezone awareness"""
    return datetime.now(timezone.utc)


def utcnow_naive() -> datetime:
    """Obtener fecha y hora actual en UTC sin timezone"""
    return datetime.utcnow()


def to_utc(dt: datetime) -> datetime:
    """Convertir datetime a UTC"""
    if dt.tzinfo is None:
        # Si no tiene timezone, asumir que es UTC
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def from_timestamp(timestamp: float) -> datetime:
    """Convertir timestamp a datetime UTC"""
    return datetime.fromtimestamp(timestamp, tz=timezone.utc)
