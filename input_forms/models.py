from django.db import models


# Create your models here.
class InputForm(models.Model):
    name = models.CharField(max_length=32)
    description = models.TextField()
    json = models.TextField()
    instructions = models.TextField()
    script = models.ForeignKey(
        "tools.ConfigTemplate",
        on_delete=models.CASCADE,
    )
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "InputForm"
        verbose_name_plural = "InputForms"
