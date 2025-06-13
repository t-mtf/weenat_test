import pytest
import uuid
from django.db import IntegrityError
from django.utils import timezone
from metrics.models import Metric


@pytest.mark.django_db
def test_create_metric_success():
    metric = Metric.objects.create(
        datalogger=uuid.uuid4(),
        at=timezone.now(),
        lat=12.34,
        lng=56.78,
        label=Metric.LabelChoices.TEMP,
        value=23.5,
    )

    assert isinstance(metric.id, uuid.UUID)
    assert metric.label == "temp"
    assert metric.value == 23.5


@pytest.mark.django_db
def test_unique_constraint_on_datalogger_at_label():
    datalogger_uuid = uuid.uuid4()
    timestamp = timezone.now()

    Metric.objects.create(
        datalogger=datalogger_uuid,
        at=timestamp,
        lat=12.0,
        lng=34.0,
        label="temp",
        value=10.0,
    )

    with pytest.raises(IntegrityError):
        Metric.objects.create(
            datalogger=datalogger_uuid,
            at=timestamp,
            lat=12.0,
            lng=34.0,
            label="temp",
            value=20.0,
        )


@pytest.mark.django_db
def test_same_datalogger_and_time_different_label_is_allowed():
    datalogger_uuid = uuid.uuid4()
    timestamp = timezone.now()

    Metric.objects.create(
        datalogger=datalogger_uuid,
        at=timestamp,
        lat=10.0,
        lng=20.0,
        label="temp",
        value=25.0,
    )
    Metric.objects.create(
        datalogger=datalogger_uuid,
        at=timestamp,
        lat=10.0,
        lng=20.0,
        label="hum",
        value=60.0,
    )

    assert Metric.objects.filter(datalogger=datalogger_uuid).count() == 2
