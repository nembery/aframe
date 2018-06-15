from __future__ import unicode_literals

from django.db import models
from input_forms.models import InputForm
import uuid


# class to hold global screen widget configuration
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
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
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


# class to hold instance screen widget data
# the same configuration can produce and consume different data
# i.e a widget to show graphs can be configured for an
# graph producer, but different data for each different instance
class ScreenWidgetData(models.Model):
    widget_type = models.CharField(max_length=64)
    name = models.CharField(max_length=64)
    data = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "ScreenWidgetData"
        verbose_name_plural = "ScreenWidgetData"


# class to hold global screen widget data
# the same configuration can produce and consume different data
# i.e a widget to show graphs can be configured for an
# graph producer via the global screen_widget_config, but different data for each different instance
# via it's screen_widget_data
class ScreenWidgetConfig(models.Model):
    widget_type = models.CharField(max_length=64)
    data = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "ScreenWidgetConfig"
        verbose_name_plural = "ScreenWidgetConfig"
