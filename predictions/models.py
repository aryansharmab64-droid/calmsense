from django.conf import settings
from django.db import models


class StressPrediction(models.Model):
    CATEGORIES = [("low", "Low stress"), ("moderate", "Moderate stress"),
                  ("high", "High stress"), ("insufficient", "Insufficient data")]
    QUALITY = [("good", "Good"), ("limited", "Limited"), ("poor", "Poor")]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="predictions")
    created_at = models.DateTimeField(auto_now_add=True)
    window_start = models.DateTimeField(null=True, blank=True)
    window_end = models.DateTimeField(null=True, blank=True)
    readings = models.ManyToManyField("sensors.SensorReading", blank=True, related_name="predictions")
    category = models.CharField(max_length=12, choices=CATEGORIES)
    probabilities = models.JSONField(default=dict, blank=True)
    model_version = models.CharField(max_length=60, blank=True)
    data_quality = models.CharField(max_length=8, choices=QUALITY, default="good")
    feature_values = models.JSONField(default=dict, blank=True)
    explanation = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "-created_at"]),
            models.Index(fields=["user", "category"]),
        ]