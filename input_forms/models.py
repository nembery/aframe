from django.db import models


# Create your models here.
class InputForm(models.Model):
    name = models.CharField(max_length=32)
    description = models.TextField()
    json = models.TextField()
    instructions = models.TextField()
    output_parser = models.CharField(max_length=64, default='default.html')
    script = models.ForeignKey(
        "tools.ConfigTemplate",
        on_delete=models.CASCADE,
    )
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "InputForm"
        verbose_name_plural = "InputForms"


class InputFormTags(models.Model):
    name = models.CharField(max_length=32)
    value = models.CharField(max_length=32)
    input_forms = models.ManyToManyField(InputForm)

