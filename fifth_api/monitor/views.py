from datetime import datetime
from typing import Any

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from ninja import NinjaAPI, Schema

from .models import Alert, Metric, Server

api = NinjaAPI(title="Server Monitoring API", version="1.0.0")


class ServerIn(Schema):
    name: str
    ip_address: str
    is_online: bool = True


class ServerOut(Schema):
    id: int
    name: str
    ip_address: str
    is_online: bool


class MetricIn(Schema):
    server_id: int
    cpu_usage: float
    memory_usage: float
    load_average: float


class MetricOut(Schema):
    id: int
    server_id: int
    cpu_usage: float
    memory_usage: float
    load_average: float

class AlertIn(Schema):
    server_id: int
    message: str


class AlertOut(Schema):
    id: int
    server_id: int
    message: str
    created_at: datetime


@api.get("/alerts", response=list[AlertOut])
@login_required
def list_alerts(request: HttpRequest) -> Any:
    """Return all metric alerts."""
    return Alert.objects.all()


@api.get("/servers", response=list[ServerOut])
@login_required
def list_servers(request: HttpRequest) -> Any:
    """Return all monitored servers."""
    return Server.objects.all()


@api.post("/servers", response=ServerOut)
@login_required
def create_server(request: HttpRequest, payload: ServerIn) -> Any:
    """Create a monitored server."""
    return Server.objects.create(**payload.dict())


@api.get("/servers/{server_id}", response=ServerOut)
@login_required
def get_server(request: HttpRequest, server_id: int) -> Any:
    """Return a single monitored server by ID."""
    return get_object_or_404(Server, id=server_id)


@api.put("/servers/{server_id}", response=ServerOut)
@login_required
def update_server(request: HttpRequest, server_id: int, payload: ServerIn) -> Any:
    """Replace a monitored server."""
    server = get_object_or_404(Server, id=server_id)
    for attr, value in payload.dict().items():
        setattr(server, attr, value)
    server.save()
    return server


@api.patch("/servers/{server_id}", response=ServerOut)
@login_required
def patch_server(request: HttpRequest, server_id: int, payload: ServerIn) -> Any:
    """Partially update a monitored server."""
    server = get_object_or_404(Server, id=server_id)
    for attr, value in payload.dict().items():
        setattr(server, attr, value)
    server.save()
    return server


@api.delete("/servers/{server_id}")
@login_required
def delete_server(request: HttpRequest, server_id: int) -> dict[str, str]:
    """Delete a monitored server."""
    server = get_object_or_404(Server, id=server_id)
    server.delete()
    return {"message": "Server deleted successfully"}


@api.get("/metrics", response=list[MetricOut])
@login_required
def list_metrics(request: HttpRequest) -> Any:
    """Return all server metrics."""
    return Metric.objects.all()


@api.post("/metrics", response=MetricOut)
@login_required
def create_metric(request: HttpRequest, payload: MetricIn) -> Any:
    """Create a metric and alert on critical values."""
    metric = Metric.objects.create(**payload.dict())
    server = metric.server

    if metric.cpu_usage >= 90:
        Alert.objects.create(server=server, message="Critical CPU usage")

    if metric.memory_usage >= 90:
        Alert.objects.create(server=server, message="Critical memory usage")

    if metric.load_average >= 80:
        Alert.objects.create(server=server, message="Critical load average")

    return metric


@api.get("/metrics/{metric_id}", response=MetricOut)
@login_required
def get_metric(request: HttpRequest, metric_id: int) -> Any:
    """Return a single metric by ID."""
    return get_object_or_404(Metric, id=metric_id)