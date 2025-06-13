from metrics import views
from django.urls import path

urlpatterns = [
    path("ingest", views.ingest_data, name="ingest"),
    path("data", views.get_raw_data, name="data"),
    path("summary", views.get_aggregated_data, name="summary"),
]
