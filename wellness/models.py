from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

User = settings.AUTH_USER_MODEL


class WellnessActivity(models.Model):
    TYPES = [("breathing", "Breathing"), ("movement", "Movement"), ("sleep", "Sleep habits"),
             ("reflection", "Reflection"), ("break", "Short break")]

    name = models.CharField(max_length=80)
    slug = models.SlugField(unique=True)
    activity_type = models.CharField(max_length=12, choices=TYPES)
    description = models.TextField()
    instructions = models.TextField()
    duration_minutes = models.PositiveSmallIntegerField(default=3)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class ActivityCompletion(models.Model):
    FEEDBACK = [("helpful", "Helpful"), ("neutral", "Neutral"), ("not_helpful", "Not helpful")]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="activity_completions")
    activity = models.ForeignKey(WellnessActivity, on_delete=models.CASCADE, related_name="completions")
    started_at = models.DateTimeField()
    completed_at = models.DateTimeField(null=True, blank=True)
    feedback = models.CharField(max_length=12, choices=FEEDBACK, blank=True)

    class Meta:
        ordering = ["-started_at"]
        indexes = [models.Index(fields=["user", "-started_at"])]


class Notification(models.Model):
    KINDS = [("simulation", "Simulation"), ("data", "Data"), ("stress", "Stress estimate"),
             ("recommendation", "Recommendation"), ("checkin", "Check-in"), ("breathing", "Breathing"),
             ("system", "System")]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    kind = models.CharField(max_length=14, choices=KINDS, default="system")
    message = models.CharField(max_length=300)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    is_dismissed = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["user", "is_dismissed", "-created_at"])]


class SleepLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sleep_logs")
    sleep_date = models.DateField()
    duration_hours = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(24)])
    quality = models.PositiveSmallIntegerField(null=True, blank=True,
                                               validators=[MinValueValidator(1), MaxValueValidator(5)])
    is_simulated = models.BooleanField(default=False)

    class Meta:
        ordering = ["-sleep_date"]
        constraints = [models.UniqueConstraint(fields=["user", "sleep_date"], name="uniq_sleep_user_date")]


class ActivityLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="activity_logs")
    date = models.DateField()
    steps = models.PositiveIntegerField(default=0)
    active_minutes = models.PositiveSmallIntegerField(default=0)
    notes = models.CharField(max_length=200, blank=True)
    is_simulated = models.BooleanField(default=False)

    class Meta:
        ordering = ["-date"]
        constraints = [models.UniqueConstraint(fields=["user", "date"], name="uniq_activity_user_date")]


class DailyCheckIn(models.Model):
    MOODS = [("calm", "Calm"), ("okay", "Okay"), ("tense", "Tense"), ("overwhelmed", "Overwhelmed")]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="checkins")
    created_at = models.DateTimeField(auto_now_add=True)
    mood = models.CharField(max_length=12, choices=MOODS)
    stress_rating = models.PositiveSmallIntegerField(null=True, blank=True,
                                                     validators=[MinValueValidator(1), MaxValueValidator(10)])
    notes = models.TextField(max_length=500, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["user", "-created_at"])]