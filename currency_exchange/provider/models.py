from django.db import models

class Provider(models.Model):
    name = models.CharField(max_length=100, unique=True)
    priority = models.PositiveIntegerField(default=0)  # Lower values mean higher priority
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ['priority']  # Default ordering by priority

    def __str__(self):
        return self.name
