from django.conf.urls import patterns, url

from tools import views


urlpatterns = patterns('',
                       url(r'^$', views.index, name='index'),
                       url(r'^new/$', views.new_template, name='new'),
                       url(r'^newTemplate/$', views.choose_action, name='choose_action'),
                       url(r'^configureAction/$', views.configure_action, name='configure_action'),
                       url(r'^defineTemplate/$', views.define_template, name='define_template'),
                       url(r'^newScript/$', views.new_script, name='new_script'),
                       url(r'^createScript/$', views.create_script, name='create_script'),
                       url(r'^viewScript/(?P<script_id>\d+)/$', views.view_script, name='view_script'),
                       url(r'^deleteScript/(?P<script_id>\d+)/$', views.delete_script, name='delete_script'),
                       url(r'^editScript/(?P<script_id>\d+)/$', views.edit_script, name='edit_script'),
                       url(r'^updateScript/$', views.update_script, name='update_script'),
                       url(r'^create/$', views.create, name='create'),
                       url(r'^update/$', views.update, name='update'),
                       url(r'^error/$', views.error, name='error'),
                       url(r'^delete/(?P<template_id>\d+)/$', views.delete, name='delete'),
                       url(r'^(?P<template_id>\d+)$', views.detail, name='detail'),
                       url(r'^edit/(?P<template_id>\d+)/$', views.edit, name='edit'),
                       url(r'^actionOptions/$', views.get_options_for_action, name='get_options_for_action'),

                       )
