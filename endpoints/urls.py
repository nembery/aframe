from django.conf.urls import url

from endpoints import views


urlpatterns = [ 
                       url(r"^$", views.index, name="index"),
                       url(r"^addEndpoints$", views.add_endpoints_to_queue, name="addEndpoints"),
                       url(r"^clearEndpoints/(?P<provider>[^/]+)/$", views.clear_endpoint_queue,
                           name="clearEndpoints"),
                       url(r"^list/(?P<group_id>[^/]+)/$", views.endpoint_list, name="list"),
                       url(r"^detail/(?P<group_id>[^/]+)/(?P<endpoint_id>[^/]+)$", views.endpoint_details,
                           name="details"),
                       url(r"^newGroup", views.new_group, name="new_group"),
                       url(r"^configureGroup", views.configure_group, name="configure_group"),
                       url(r"^createGroup", views.create_group, name="create_group"),
                       url(r"^deleteGroup/(?P<group_id>[^/]+)/$", views.delete_group,
                           name="delete_group"),

                       ]
