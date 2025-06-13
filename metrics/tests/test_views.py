from datetime import timedelta
from django.utils import timezone
import uuid

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from metrics.models import Metric


@pytest.mark.django_db
def test_ingest_data_success():
    client = APIClient()
    url = reverse("ingest")
    payload = {
        "at": "2024-05-01T10:00:00Z",
        "datalogger": str(uuid.uuid4()),
        "location": {"lat": 45.0, "lng": 3.0},
        "measurements": [
            {"label": "temp", "value": 20.5},
            {"label": "hum", "value": 55.2},
        ],
    }

    response = client.post(url, payload, format="json")

    assert response.status_code == status.HTTP_200_OK
    assert Metric.objects.count() == 2


@pytest.mark.django_db
def test_ingest_data_duplicate():
    client = APIClient()
    datalogger_uuid = uuid.uuid4()
    at = "2024-05-01T10:00:00Z"

    Metric.objects.create(
        datalogger=datalogger_uuid,
        at=at,
        lat=45.0,
        lng=3.0,
        label="temp",
        value=20.0,
    )

    payload = {
        "at": at,
        "datalogger": str(datalogger_uuid),
        "location": {"lat": 45.0, "lng": 3.0},
        "measurements": [{"label": "temp", "value": 21.0}],
    }

    response = client.post(reverse("ingest"), payload, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Duplicate label" in response.data.get("detail")


@pytest.mark.django_db
def test_get_raw_data_success():
    client = APIClient()
    datalogger_uuid = uuid.uuid4()
    _ = Metric.objects.create(
        datalogger=datalogger_uuid,
        at=timezone.now(),
        lat=10.0,
        lng=20.0,
        label="temp",
        value=23.0,
    )

    url = reverse("data") + f"?datalogger={datalogger_uuid}"
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data[0]["label"] == "temp"


@pytest.mark.django_db
def test_get_raw_data_missing_datalogger():
    client = APIClient()
    response = client.get(reverse("data"))
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Missing datalogger" in response.data.get("error")


@pytest.mark.django_db
def test_get_aggregated_data_hour_sum_and_avg():
    client = APIClient()
    datalogger_uuid = uuid.uuid4()
    now = timezone.now().replace(minute=0, second=0, microsecond=0)

    Metric.objects.bulk_create(
        [
            Metric(
                datalogger=datalogger_uuid,
                at=now,
                lat=1,
                lng=2,
                label="temp",
                value=10.0,
            ),
            Metric(
                datalogger=datalogger_uuid,
                at=now + timedelta(minutes=1),
                lat=1,
                lng=2,
                label="temp",
                value=20.0,
            ),
            Metric(
                datalogger=datalogger_uuid,
                at=now,
                lat=1,
                lng=2,
                label="rain",
                value=5.0,
            ),
            Metric(
                datalogger=datalogger_uuid,
                at=now + timedelta(minutes=1),
                lat=1,
                lng=2,
                label="rain",
                value=10.0,
            ),
        ]
    )

    url = reverse("summary") + f"?datalogger={datalogger_uuid}&span=hour"
    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK

    results = {item.get("label"): item.get("value") for item in response.data}
    assert results.get("temp") == 15.0
    assert results.get("rain") == 15.0


@pytest.mark.django_db
def test_get_aggregated_data_raw_fallback():
    client = APIClient()
    datalogger_uuid = uuid.uuid4()
    Metric.objects.create(
        datalogger=datalogger_uuid,
        at=timezone.now(),
        lat=1.0,
        lng=2.0,
        label="hum",
        value=45.5,
    )

    url = reverse("summary") + f"?datalogger={datalogger_uuid}&span=invalid"
    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data[0].get("label") == "hum"
