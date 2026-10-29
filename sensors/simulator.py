import math
import random
from dataclasses import dataclass

from .validators import FIELD_RULES


@dataclass(frozen=True)
class Scenario:
    key: str
    label: str
    description: str
    hr: float
    hrv: float
    temp: float
    eda: float
    hr_sd: float
    hrv_sd: float
    temp_sd: float
    eda_sd: float
    steps: tuple
    missing_prob: float = 0.03
    recovery: bool = False


SCENARIOS = {
    s.key: s
    for s in [
        Scenario("relaxed", "Relaxed day",
                 "Synthetic: steady heart rate, higher HRV, low electrodermal activity.",
                 66, 62, 33.6, 1.6, 2.5, 6, 0.15, 0.25, (0, 30)),
        Scenario("busy", "Busy workday",
                 "Synthetic: raised heart rate, reduced HRV, higher EDA.",
                 82, 34, 33.1, 5.0, 3.5, 6, 0.20, 0.80, (0, 60), 0.04),
        Scenario("poor_sleep", "Poor sleep",
                 "Synthetic: mildly raised heart rate and lowered HRV with little movement.",
                 77, 38, 33.4, 3.4, 3.0, 7, 0.20, 0.60, (0, 20), 0.05),
        Scenario("post_exercise", "Post-exercise recovery",
                 "Synthetic: values start elevated and settle over time. High heart rate here is not stress.",
                 70, 52, 33.5, 2.0, 2.5, 5, 0.12, 0.30, (10, 80), 0.02, True),
        Scenario("mixed", "Mixed physiological signals",
                 "Synthetic: conflicting signals (high heart rate, normal HRV, low EDA) and more gaps.",
                 85, 56, 33.9, 1.7, 5.0, 10, 0.30, 0.50, (0, 40), 0.08),
    ]
}
SCENARIO_CHOICES = [(k, s.label) for k, s in SCENARIOS.items()]


def _clamp(value, name):
    low, high, _ = FIELD_RULES[name]
    return min(max(value, low), high)


def generate_reading(scenario_key, tick=0, rng=None, timestamp=None):
    """Return one synthetic reading payload (a dict accepted by validate_reading)."""
    sc = SCENARIOS[scenario_key]
    rng = rng or random

    if sc.recovery:
        f = math.exp(-tick / 40.0)
        hr = sc.hr + 56 * f + rng.gauss(0, sc.hr_sd)
        hrv = sc.hrv - 28 * f + rng.gauss(0, sc.hrv_sd)
        temp = sc.temp + 1.0 * f + rng.gauss(0, sc.temp_sd)
        eda = sc.eda + 4.0 * f + rng.gauss(0, sc.eda_sd)
        steps = int(rng.randint(*sc.steps) * (0.2 + f))
    else:
        drift = math.sin(tick / 9.0)
        hr = sc.hr + 3.0 * drift + rng.gauss(0, sc.hr_sd)
        # mild, imperfect inverse coupling between heart rate and HRV
        hrv = sc.hrv - 2.5 * drift - 0.3 * (hr - sc.hr) + rng.gauss(0, sc.hrv_sd)
        temp = sc.temp + 0.15 * drift + rng.gauss(0, sc.temp_sd)
        eda = sc.eda + 0.4 * drift + rng.gauss(0, sc.eda_sd)
        if rng.random() < 0.06:
            eda += rng.uniform(1.0, 3.0)  # occasional EDA response
        steps = rng.randint(*sc.steps)

    values = {
        "heart_rate": round(_clamp(hr, "heart_rate"), 1),
        "hrv_ms": round(_clamp(hrv, "hrv_ms"), 1),
        "skin_temp_c": round(_clamp(temp, "skin_temp_c"), 2),
        "eda_us": round(_clamp(eda, "eda_us"), 2),
    }
    # sensor dropouts
    for key in list(values):
        if rng.random() < sc.missing_prob:
            values[key] = None
    if all(v is None for v in values.values()):
        values["heart_rate"] = round(_clamp(hr, "heart_rate"), 1)

    values["steps"] = max(0, steps)
    if timestamp is not None:
        values["timestamp"] = timestamp.isoformat()
    return values