from django.db import IntegrityError, transaction

from .models import SensorReading
from .validators import validate_reading


class DuplicateReading(Exception):
    pass


def build_reading(user, payload, *, source, is_simulated=False, scenario=""):
    """Validate a payload and return an unsaved SensorReading."""
    cleaned = validate_reading(payload)
    return SensorReading(user=user, source=source, is_simulated=is_simulated, scenario=scenario, **cleaned)


def ingest_reading(user, payload, *, source, is_simulated=False, scenario=""):
    """Single entry point for every reading (simulator, manual form, future device bridge)."""
    reading = build_reading(user, payload, source=source, is_simulated=is_simulated, scenario=scenario)
    if SensorReading.objects.filter(user=user, timestamp=reading.timestamp, source=source).exists():
        raise DuplicateReading("A reading with this timestamp already exists for this source.")
    try:
        with transaction.atomic():
            reading.save()
    except IntegrityError:
        raise DuplicateReading("A reading with this timestamp already exists for this source.")
    return reading


def serialize_reading(r):
    return {
        "id": r.pk,
        "timestamp": r.timestamp.isoformat(),
        "heart_rate": r.heart_rate,
        "hrv_ms": r.hrv_ms,
        "skin_temp_c": r.skin_temp_c,
        "eda_us": r.eda_us,
        "steps": r.steps,
        "source": r.source,
        "is_simulated": r.is_simulated,
        "scenario": r.scenario,
        "quality": r.quality,
    }