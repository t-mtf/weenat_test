from typing import List

from django.db import IntegrityError

from metrics.models import Metric
from metrics.serializers import (
    IngestSerializer,
    MeasurementAggregateSerializer,
    MeasurementOutputSerializer,
)
from rest_framework.decorators import api_view
from django.db.models.functions import TruncHour, TruncDay
from django.db.models import Avg, Sum
from rest_framework import status
from rest_framework.response import Response


@api_view(["POST"])
def ingest_data(request):
    serializer = IngestSerializer(data=request.data)
    if serializer.is_valid():
        data = serializer.validated_data
        at = data.get("at")
        datalogger = data.get("datalogger")
        lat = data.get("location").get("lat")
        lng = data.get("location").get("lng")

        metrics: List[Metric] = [
            Metric(
                at=at,
                datalogger=datalogger,
                lat=lat,
                lng=lng,
                label=measurement.get("label"),
                value=measurement.get("value"),
            )
            for measurement in data.get("measurements")
        ]
        try:
            Metric.objects.bulk_create(metrics)
        except IntegrityError as e:
            return Response(
                {
                    "detail": f"Duplicate label for the same record is not allowed. {str(e)}"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(
            {"message": "Record is inserted successfully"}, status=status.HTTP_200_OK
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def fetch_raw_metrics(request):
    since = request.GET.get("since")
    before = request.GET.get("before")
    datalogger = request.GET.get("datalogger")

    if not datalogger:
        return None, Response(
            {"error": "Missing datalogger"}, status=status.HTTP_400_BAD_REQUEST
        )

    queryset = Metric.objects.filter(datalogger=datalogger)
    if since:
        queryset = queryset.filter(at__gt=since)
    if before:
        queryset = queryset.filter(at__lt=before)

    return queryset, None


@api_view(["GET"])
def get_raw_data(request):
    queryset, error_response = fetch_raw_metrics(request)
    if error_response:
        return error_response

    serializer = MeasurementOutputSerializer(queryset, many=True)
    return Response(serializer.data)


@api_view(["GET"])
def get_aggregated_data(request):
    queryset, error_response = fetch_raw_metrics(request)
    if error_response:
        return error_response

    span = request.GET.get("span", "raw")

    if span == "hour":
        truncate = TruncHour("at")
    elif span == "day":
        truncate = TruncDay("at")
    else:
        serializer = MeasurementOutputSerializer(queryset, many=True)
        return Response(serializer.data)

    results = []
    for label in Metric.LabelChoices.values:
        aggregated_queryset = queryset.filter(label=label)
        if label == str(Metric.LabelChoices.RAIN):
            agg_func = Sum("value")
        else:
            agg_func = Avg("value")

        grouped = (
            aggregated_queryset.annotate(time_slot=truncate)
            .values("time_slot")
            .annotate(value=agg_func)
            .order_by("time_slot")
        )
        for item in grouped:
            results.append(
                {
                    "label": label,
                    "time_slot": item.get("time_slot"),
                    "value": round(item.get("value"), 2),
                }
            )

    serializer = MeasurementAggregateSerializer(results, many=True)
    return Response(serializer.data)
