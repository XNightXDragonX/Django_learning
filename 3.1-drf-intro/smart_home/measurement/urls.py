from django.urls import path
from .views import (
    SensorView,
    SensorUpdateView,
    SensorDetailView,
    MeasurementView
)


urlpatterns = [
    path('sensors/', SensorView.as_view()),
    path('sensors/<pk>/', SensorUpdateView.as_view()),
    path('sensors/<pk>/detail/', SensorDetailView.as_view()),
    path('measurements/', MeasurementView.as_view())
]
