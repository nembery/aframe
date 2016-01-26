from django.conf.urls import patterns, url

from endpoints import views


urlpatterns = patterns('',
                       url(r'^$', views.index, name='index'),
                       url(r'^addEndpoints$', views.add_endpoints_to_job, name='addEndpoints'),
                       url(r'^clearEndpoints/(?P<provider>[^/]+)/$', views.clear_job_endpoints, name='clearEndpoints'),
                       url(r'^list/(?P<provider>[^/]+)/$', views.endpoint_list, name='list'),
                       url(r'^detail/(?P<provider>[^/]+)/(?P<endpoint_id>[^/]+)$', views.endpoint_details,
                           name='details'),
                       )
