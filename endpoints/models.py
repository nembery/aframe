from django.db import models


# Create your models here.
class EndpointGroup(models.Model):
    name = models.CharField(max_length=32)
    description = models.TextField()
    provider_class = models.CharField(max_length=32)
    provider_configuration = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "EndpointGroup"
        verbose_name_plural = "EndpointGroups"

