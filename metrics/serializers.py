from metrics.models import Metric
from rest_framework import serializers


class MeasurementInputSerializer(serializers.Serializer):
    label = serializers.ChoiceField(choices=Metric.LabelChoices.choices)
    value = serializers.FloatField()


class LocationSerializer(serializers.Serializer):
    lat = serializers.FloatField()
    lng = serializers.FloatField()


class IngestSerializer(serializers.Serializer):
    at = serializers.DateTimeField()
    datalogger = serializers.UUIDField()
    location = LocationSerializer(required=True)
    measurements = serializers.ListSerializer(
        child=MeasurementInputSerializer(), allow_empty=False
    )


class MeasurementOutputSerializer(serializers.Serializer):
    label = serializers.CharField()
    measured_at = serializers.DateTimeField(source="at")
    value = serializers.FloatField()


class MeasurementAggregateSerializer(serializers.Serializer):
    label = serializers.CharField()
    time_slot = serializers.DateTimeField()
    value = serializers.FloatField()
