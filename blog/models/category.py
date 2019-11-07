from rest_framework import serializers
from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=25, unique=True, blank=False, null=False)

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name
