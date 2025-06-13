import uuid
from django.db import models


class Metric(models.Model):
    class LabelChoices(models.TextChoices):
        TEMP = "temp", "Temperature"
        RAIN = "rain", "Rain"
        HUM = "hum", "Humidity"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    datalogger = models.UUIDField()
    at = models.DateTimeField()
    lat = models.FloatField()
    lng = models.FloatField()

    label = models.CharField(max_length=10, choices=LabelChoices.choices)
    value = models.FloatField()

    class Meta:
        indexes = [models.Index(fields=["datalogger", "at"])]
        constraints = [
            models.UniqueConstraint(
                fields=["datalogger", "at", "label"],
                name="unique_metric_per_datalogger_time_label",
            )
        ]
