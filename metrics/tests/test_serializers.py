import uuid

from metrics.serializers import (
    IngestSerializer,
    MeasurementInputSerializer,
    LocationSerializer,
)


def test_valid_location_serializer():
    data = {"lat": 48.8566, "lng": 2.3522}
    serializer = LocationSerializer(data=data)
    assert serializer.is_valid()


def test_invalid_location_serializer():
    data = {"lat": "not_a_float", "lng": 2.3522}
    serializer = LocationSerializer(data=data)
    assert not serializer.is_valid()


def test_valid_measurement_input_serializer():
    data = {"label": "temp", "value": 22.3}
    serializer = MeasurementInputSerializer(data=data)
    assert serializer.is_valid()


def test_invalid_measurement_label():
    data = {"label": "invalid", "value": 22.3}
    serializer = MeasurementInputSerializer(data=data)
    assert not serializer.is_valid()


def test_valid_ingest_serializer():
    data = {
        "at": "2024-06-01T10:00:00Z",
        "datalogger": str(uuid.uuid4()),
        "location": {"lat": 45.0, "lng": 3.0},
        "measurements": [{"label": "temp", "value": 20.5}],
    }
    serializer = IngestSerializer(data=data)
    assert serializer.is_valid()


def test_invalid_ingest_serializer_missing_measurements():
    data = {
        "at": "2024-06-01T10:00:00Z",
        "datalogger": str(uuid.uuid4()),
        "location": {"lat": 45.0, "lng": 3.0},
        "measurements": [],
    }
    serializer = IngestSerializer(data=data)
    assert not serializer.is_valid()
