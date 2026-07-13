from django.db import models


class Server(models.Model):
    name = models.CharField(max_length=255)
    ip_address = models.GenericIPAddressField()
    is_online = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} - {self.ip_address}"


class Metric(models.Model):
    server = models.ForeignKey(Server, on_delete=models.CASCADE, related_name="metrics")
    cpu_usage = models.FloatField()
    memory_usage = models.FloatField()
    load_average = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)


class Alert(models.Model):
    server = models.ForeignKey(Server, on_delete=models.CASCADE, related_name="alerts")
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
