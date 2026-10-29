from django.conf import settings
from django.db import models

from .simulator import SCENARIO_CHOICES


class SensorReading(models.Model):
    SOURCES = [
        ("simulation", "Simulation (synthetic)"),
        ("manual", "Manual entry"),
        ("device_api", "Device / API input"),
    ]
    QUALITY = [("complete", "Complete"), ("partial", "Partial")]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sensor_readings")
    timestamp = models.DateTimeField()
    heart_rate = models.FloatField(null=True, blank=True, help_text="BPM")
    hrv_ms = models.FloatField(null=True, blank=True, help_text="Heart rate variability, ms")
    skin_temp_c = models.FloatField(null=True, blank=True, help_text="°C")
    eda_us = models.FloatField(null=True, blank=True, help_text="Electrodermal activity, µS")
    steps = models.PositiveIntegerField(null=True, blank=True, help_text="Steps since previous reading")
    source = models.CharField(max_length=12, choices=SOURCES, default="simulation")
    is_simulated = models.BooleanField(default=False)
    scenario = models.CharField(max_length=20, blank=True)
    quality = models.CharField(max_length=10, choices=QUALITY, default="complete")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["user", "-timestamp"]),
            models.Index(fields=["user", "is_simulated"]),
        ]
        constraints = [
            models.UniqueConstraint(fields=["user", "timestamp", "source"], name="uniq_reading_user_ts_source"),
        ]

    def __str__(self):
        return f"{self.user.username} @ {self.timestamp:%Y-%m-%d %H:%M:%S}"


class SimulationState(models.Model):
    STATUS = [("stopped", "Stopped"), ("running", "Running"), ("paused", "Paused")]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="simulation_state")
    status = models.CharField(max_length=8, choices=STATUS, default="stopped")
    scenario = models.CharField(max_length=20, choices=SCENARIO_CHOICES, default="relaxed")
    tick = models.PositiveIntegerField(default=0)
    readings_generated = models.PositiveIntegerField(default=0)
    started_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}: {self.status} ({self.scenario})"
