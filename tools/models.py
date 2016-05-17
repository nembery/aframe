from django.db import models
from django import forms
from django.forms import ModelForm
from django.views.generic.edit import UpdateView


class ConfigTemplate(models.Model):
    type_choices = (("standalone", "Standalone"), ("per-endpoint", "Per-Endpoint"))
    name = models.CharField(max_length=32)
    description = models.TextField()
    template = models.TextField()
    action_provider = models.CharField(max_length=64)
    action_provider_options = models.CharField(max_length=512)
    type = models.CharField(max_length=32, choices=type_choices, default="standalone")
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "ConfigTemplate"
        verbose_name_plural = "configTemplates"


class ConfigTemplateForm(ModelForm):
    description = forms.CharField(widget=forms.Textarea(attrs={"rows": "2"}))
    template = forms.CharField(widget=forms.Textarea(attrs={"rows": "20", "title": "Configuration Template"}))
    action_provider_options = forms.CharField(widget=forms.Textarea(attrs={"rows": "20",
                                                                           "title": "Provider Options Debug"}))

    class Meta:
        model = ConfigTemplate
        fields = ["name", "description", "template", "action_provider_options"]


class ConfigTemplateUpdate(UpdateView):
    model = ConfigTemplate
    fields = ["name", "description", "template"]
    template_name_suffix = "_update_form"


class Script(models.Model):
    type_choices = (("ssh", "On-Box"), ("netconf", "Off-Box"))

    name = models.CharField(max_length=32)
    description = models.TextField()
    script = models.TextField()
    type = models.CharField(max_length=32, choices=type_choices, default="netconf")
    destination = models.CharField(max_length=256)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "script"
        verbose_name_plural = "scripts"


class ScriptForm(ModelForm):
    description = forms.CharField(widget=forms.Textarea(attrs={"rows": "3"}))
    script = forms.CharField(widget=forms.Textarea(attrs={"rows": "40", "title": "Script"}))

    class Meta:
        model = Script
        fields = ["name", "description",  "destination", "type", "script"]


class ScriptUpdate(UpdateView):
    model = Script
    fields = ["name", "description", "destination", "script"]
    template_name_suffix = "_update_form"
