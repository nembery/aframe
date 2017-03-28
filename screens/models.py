from __future__ import unicode_literals

from django.db import models
from input_forms.models import InputForm


class ScreenWidget(models.Model):
    name = models.CharField(max_length=32)
    description = models.TextField()
    configuration = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "ScreenWidget"
        verbose_name_plural = "ScreenWidgets"


class Screen(models.Model):
    name = models.CharField(max_length=32)
    description = models.TextField()
    input_forms = models.ManyToManyField(InputForm)
    screen_widgets = models.ManyToManyField(ScreenWidget)
    layout = models.TextField()
    theme = models.CharField(max_length=32)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Screen"
        verbose_name_plural = "Screens"

