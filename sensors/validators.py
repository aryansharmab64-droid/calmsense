import math
from datetime import datetime, timedelta

from django.utils import timezone
from django.utils.dateparse import parse_datetime

# name: (min, max, unit)
FIELD_RULES = {
    "heart_rate": (30.0, 220.0, "BPM"),
    "hrv_ms": (5.0, 250.0, "ms"),
    "skin_temp_c": (25.0, 40.0, "°C"),
    "eda_us": (0.01, 60.0, "µS"),
}
STEPS_MAX = 10000
FUTURE_TOLERANCE = timedelta(minutes=5)
MAX_AGE = timedelta(days=365)


class ValidationFailure(Exception):
    """Raised with a {field: message} dict when a reading is malformed."""

    def __init__(self, errors):
        self.errors = errors
        super().__init__("; ".join(f"{k}: {v}" for k, v in errors.items()))


def _to_number(name, value, errors):
    if value is None or value == "":
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float, str)):
        errors[name] = "Must be a number."
        return None
    try:
        number = float(value)
    except ValueError:
        errors[name] = "Must be a number."
        return None
    if math.isnan(number) or math.isinf(number):
        errors[name] = "Must be a finite number."
        return None
    return number


def validate_reading(payload):
    """Validate one reading and return a cleaned dict ready for SensorReading(**cleaned)."""
    if not isinstance(payload, dict):
        raise ValidationFailure({"payload": "A reading must be a JSON object."})

    errors = {}
    now = timezone.now()

    # Timestamp
    raw_ts = payload.get("timestamp")
    ts = None
    if raw_ts in (None, ""):
        ts = now
    elif isinstance(raw_ts, datetime):
        ts = raw_ts
    elif isinstance(raw_ts, str):
        try:
            ts = parse_datetime(raw_ts)
        except ValueError:
            ts = None
        if ts is None:
            errors["timestamp"] = "Use ISO 8601, e.g. 2026-10-28T09:30:00+05:30."
    else:
        errors["timestamp"] = "Must be an ISO 8601 string."
    if ts is not None:
        if timezone.is_naive(ts):
            ts = timezone.make_aware(ts)
        if ts > now + FUTURE_TOLERANCE:
            errors["timestamp"] = "Timestamp cannot be in the future."
        elif ts < now - MAX_AGE:
            errors["timestamp"] = "Timestamp is more than one year old."

    # Physiological measurements
    cleaned = {}
    for name, (low, high, unit) in FIELD_RULES.items():
        value = _to_number(name, payload.get(name), errors)
        if value is not None and name not in errors and not (low <= value <= high):
            errors[name] = f"Must be between {low:g} and {high:g} {unit}."
            value = None
        cleaned[name] = value

    # Steps taken since the previous reading
    steps = _to_number("steps", payload.get("steps"), errors)
    if steps is not None and "steps" not in errors:
        if steps != int(steps):
            errors["steps"] = "Must be a whole number."
            steps = None
        elif not (0 <= steps <= STEPS_MAX):
            errors["steps"] = f"Must be between 0 and {STEPS_MAX}."
            steps = None
        else:
            steps = int(steps)
    cleaned["steps"] = steps

    if not errors and all(cleaned[k] is None for k in cleaned):
        errors["readings"] = "Provide at least one measurement."

    if errors:
        raise ValidationFailure(errors)

    physio_present = all(cleaned[k] is not None for k in FIELD_RULES)
    cleaned["timestamp"] = ts
    cleaned["quality"] = "complete" if physio_present else "partial"
    return cleaned