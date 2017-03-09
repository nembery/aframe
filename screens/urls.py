from django.conf.urls import url

from screens import views

urlpatterns = [
    url(r"^$", views.index,
        name="index"),
    url(r"^create$", views.create,
        name="create"),
    url(r"^update$", views.update,
        name="update"),
    url(r"^updateLayout", views.update_layout,
        name="update_layout"),
    url(r"^delete/(?P<screen_id>[0-9]+)/$", views.delete,
        name="delete"),
    url(r"^edit/(?P<screen_id>[0-9]+)/$", views.edit,
        name="edit"),
    url(r"^(?P<screen_id>[0-9]+)$", views.detail,
        name="detail"),

    url(r"^new$", views.new,
        name="new")
]
