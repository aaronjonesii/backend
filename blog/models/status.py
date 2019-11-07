from django.db import models


class Status(models.Model):
    name = models.CharField(max_length=25, unique=True, blank=False)

    class Meta:
        verbose_name = "Status"
        verbose_name_plural = "Statuses"

    def __str__(self):
        return self.name
