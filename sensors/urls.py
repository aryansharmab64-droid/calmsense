from django.urls import path

from . import views

urlpatterns = [
    path("monitor/", views.monitor, name="monitor"),
    path("api/sensors/state/", views.sensor_state, name="api_sensor_state"),
    path("api/sensors/simulation/", views.simulation_control, name="api_sim_control"),
    path("api/sensors/poll/", views.simulation_poll, name="api_sim_poll"),
    path("api/sensors/generate/", views.simulation_generate, name="api_sim_generate"),
    path("api/sensors/reset/", views.simulation_reset, name="api_sim_reset"),
    path("api/sensors/ingest/", views.sensor_ingest, name="api_sensor_ingest"),
    path("api/sensors/readings/", views.sensor_readings, name="api_sensor_readings"),
]