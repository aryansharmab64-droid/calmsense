from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class UserProfile(models.Model):
    AGE_RANGES = [
        ("", "Prefer not to say"),
        ("under_18", "Under 18"),
        ("18_24", "18–24"),
        ("25_34", "25–34"),
        ("35_49", "35–49"),
        ("50_plus", "50+"),
    ]
    UNITS = [("metric", "Metric (°C)"), ("imperial", "Imperial (°F)")]
    RANGES = [("today", "Today"), ("7d", "Last 7 days"), ("30d", "Last 30 days")]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    display_name = models.CharField(max_length=60, blank=True)
    age_range = models.CharField(max_length=12, choices=AGE_RANGES, blank=True)
    preferred_units = models.CharField(max_length=10, choices=UNITS, default="metric")
    wellness_goals = models.TextField(max_length=400, blank=True)
    resting_hr_baseline = models.PositiveSmallIntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(35), MaxValueValidator(120)],
        help_text="Optional. Typical resting heart rate in BPM.",
    )
    default_range = models.CharField(max_length=5, choices=RANGES, default="7d")
    notify_checkin = models.BooleanField(default=True)
    notify_stress = models.BooleanField(default=True)
    notify_data = models.BooleanField(default=True)
    consent_optional_data = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Profile of {self.user.username}"

    @property
    def name(self):
        return self.display_name or self.user.first_name or self.user.username