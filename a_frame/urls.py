from django.conf.urls import patterns, include, url
import views

urlpatterns = patterns("",
                       url(r"^tools/", include("tools.urls", namespace="script")),
                       url(r"^endpoints/", include("endpoints.urls", namespace="endpoint")),
                       url(r"^input_forms/", include("input_forms.urls", namespace="inputForms")),
                       url(r"^$", views.index, name="index"),
                       )

