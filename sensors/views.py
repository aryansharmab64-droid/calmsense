import json
from datetime import timedelta
from functools import wraps

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_GET, require_POST

from wellness.models import Notification

from .models import SensorReading, SimulationState
from .services import DuplicateReading, build_reading, ingest_reading, serialize_reading
from .simulator import SCENARIOS, generate_reading
from .validators import ValidationFailure

METRICS = [
    ("heart_rate", "Heart rate", "BPM", "bi-heart-pulse"),
    ("hrv_ms", "HRV", "ms", "bi-activity"),
    ("skin_temp_c", "Skin temperature", "°C", "bi-thermometer-half"),
    ("eda_us", "EDA", "µS", "bi-droplet"),
    ("steps", "Steps (per reading)", "steps", "bi-person-walking"),
]
POLL_MS = 5000


class ApiError(Exception):
    def __init__(self, message, status=400):
        self.message = message
        self.status = status


def api(view):
    """JSON endpoint wrapper: 401 for anonymous users and consistent error bodies."""
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({"error": "Authentication required."}, status=401)
        try:
            return view(request, *args, **kwargs)
        except ApiError as exc:
            return JsonResponse({"error": exc.message}, status=exc.status)
        except ValidationFailure as exc:
            return JsonResponse({"error": "Validation failed.", "fields": exc.errors}, status=422)
        except DuplicateReading as exc:
            return JsonResponse({"error": str(exc)}, status=409)
    return wrapper


def _body(request):
    if not request.body:
        return {}
    try:
        data = json.loads(request.body)
    except ValueError:
        raise ApiError("Request body must be valid JSON.")
    if not isinstance(data, dict):
        raise ApiError("JSON body must be an object.")
    return data


def _int_param(value, name, default, low, high):
    if value is None:
        return default
    if isinstance(value, bool):
        raise ApiError(f"{name} must be a whole number.")
    try:
        number = int(value)
    except (TypeError, ValueError):
        raise ApiError(f"{name} must be a whole number.")
    if not low <= number <= high:
        raise ApiError(f"{name} must be between {low} and {high}.")
    return number


def _state_payload(user):
    state, _ = SimulationState.objects.get_or_create(user=user)
    recent = list(SensorReading.objects.filter(user=user).order_by("-timestamp")[:30])
    latest = recent[0] if recent else None
    age = int((timezone.now() - latest.timestamp).total_seconds()) if latest else None
    scenario = SCENARIOS.get(state.scenario, SCENARIOS["relaxed"])
    return {
        "simulation": {
            "status": state.status,
            "scenario": scenario.key,
            "scenario_label": scenario.label,
            "readings_generated": state.readings_generated,
            "tick": state.tick,
        },
        "latest": serialize_reading(latest) if latest else None,
        "latest_age_seconds": age,
        "readings": [serialize_reading(r) for r in reversed(recent)],
        "total_readings": SensorReading.objects.filter(user=user).count(),
    }


@login_required
@ensure_csrf_cookie
def monitor(request):
    state, _ = SimulationState.objects.get_or_create(user=request.user)
    scenarios = [{"key": s.key, "label": s.label, "description": s.description} for s in SCENARIOS.values()]
    return render(request, "sensors/monitor.html", {
        "scenarios": scenarios,
        "metrics": METRICS,
        "poll_ms": POLL_MS,
        "current_scenario": state.scenario,
    })


@require_GET
@api
def sensor_state(request):
    return JsonResponse(_state_payload(request.user))


@require_POST
@api
def simulation_control(request):
    data = _body(request)
    action = data.get("action")
    scenario = data.get("scenario")
    if scenario is not None and scenario not in SCENARIOS:
        raise ApiError("Unknown scenario.")

    state, _ = SimulationState.objects.get_or_create(user=request.user)

    if action == "start":
        state.status, state.tick, state.readings_generated = "running", 0, 0
        state.started_at = timezone.now()
        if scenario:
            state.scenario = scenario
    elif action == "pause":
        if state.status != "running":
            raise ApiError("The simulation is not running.", 409)
        state.status = "paused"
    elif action == "resume":
        if state.status != "paused":
            raise ApiError("The simulation is not paused.", 409)
        state.status = "running"
    elif action == "stop":
        if state.status == "stopped":
            raise ApiError("The simulation is already stopped.", 409)
        state.status = "stopped"
        Notification.objects.create(
            user=request.user,
            kind="simulation",
            message=(f"Simulation finished. {state.readings_generated} synthetic readings were generated "
                     f"in the \u201c{SCENARIOS[state.scenario].label}\u201d scenario."),
        )
    elif action == "set_scenario":
        if not scenario:
            raise ApiError("Choose a scenario.")
        state.scenario, state.tick = scenario, 0
    else:
        raise ApiError("Unknown action.")

    state.save()
    return JsonResponse(_state_payload(request.user))


@require_POST
@api
def simulation_poll(request):
    """Called by the browser every few seconds. Creates one synthetic reading while running."""
    state, _ = SimulationState.objects.get_or_create(user=request.user)
    if state.status == "running":
        payload = generate_reading(state.scenario, state.tick, timestamp=timezone.now())
        try:
            ingest_reading(request.user, payload, source="simulation", is_simulated=True, scenario=state.scenario)
        except DuplicateReading:
            pass
        state.tick += 1
        state.readings_generated += 1
        state.save()
    return JsonResponse(_state_payload(request.user))


@require_POST
@api
def simulation_generate(request):
    data = _body(request)
    count = _int_param(data.get("count"), "count", 10, 1, 60)
    state, _ = SimulationState.objects.get_or_create(user=request.user)
    now = timezone.now()
    objs = []
    for i in range(count):
        ts = now - timedelta(minutes=count - 1 - i)
        payload = generate_reading(state.scenario, i, timestamp=ts)
        objs.append(build_reading(request.user, payload, source="simulation",
                                  is_simulated=True, scenario=state.scenario))
    SensorReading.objects.bulk_create(objs, ignore_conflicts=True)
    state.readings_generated += count
    state.save()
    return JsonResponse(_state_payload(request.user), status=201)


@require_POST
@api
def simulation_reset(request):
    """Deletes only this user's simulated readings. Manual and device readings are kept."""
    qs = SensorReading.objects.filter(user=request.user, is_simulated=True)
    deleted = qs.count()
    qs.delete()
    SimulationState.objects.filter(user=request.user).update(
        status="stopped", tick=0, readings_generated=0, started_at=None)
    payload = _state_payload(request.user)
    payload["deleted"] = deleted
    return JsonResponse(payload)


@require_POST
@api
def sensor_ingest(request):
    """Structured ingestion interface (session + CSRF protected)."""
    data = _body(request)
    source = data.pop("source", "device_api")
    if source not in ("manual", "device_api"):
        raise ApiError("source must be 'manual' or 'device_api'.")
    reading = ingest_reading(request.user, data, source=source, is_simulated=False)
    return JsonResponse({"reading": serialize_reading(reading)}, status=201)


@require_GET
@api
def sensor_readings(request):
    rng = request.GET.get("range", "7d")
    if rng not in ("today", "7d", "30d"):
        raise ApiError("range must be one of: today, 7d, 30d.")
    limit = _int_param(request.GET.get("limit"), "limit", 200, 1, 1000)
    start = timezone.localtime().replace(hour=0, minute=0, second=0, microsecond=0)
    if rng == "7d":
        start -= timedelta(days=6)
    elif rng == "30d":
        start -= timedelta(days=29)
    qs = SensorReading.objects.filter(user=request.user, timestamp__gte=start).order_by("-timestamp")[:limit]
    return JsonResponse({"range": rng, "readings": [serialize_reading(r) for r in reversed(list(qs))]})
