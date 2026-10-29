from django.contrib import admin

from .models import SensorReading, SimulationState


@admin.register(SensorReading)
class SensorReadingAdmin(admin.ModelAdmin):
    list_display = ("user", "timestamp", "source", "is_simulated", "quality")
    list_filter = ("source", "is_simulated", "quality")


@admin.register(SimulationState)
class SimulationStateAdmin(admin.ModelAdmin):
    list_display = ("user", "status", "scenario", "updated_at")
