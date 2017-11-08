from django.conf.urls import url
from . import views
from django.contrib import admin

admin.autodiscover()

urlpatterns = [
    url(r'^create/', views.create_comment, name='create_comment'),
    url(r'^all_comments/(?:(?P<active_type>[\w\-]+)/)?', views.get_all_comments, name='get_all_comments'),
    url(r'^more_comments/(?:type-(?P<comments_type>[\w\-]+)/)?$', views.get_more_comments, name='get_more_comments'),
    url(r'^mark_as_moderated/(?:pk-(?P<pk>[\w\-]+)/)?$', views.mark_as_moderated, name='mark_as_moderated'),
    url(r'^moderate/(?:pk-(?P<pk>[\w\-]+)/)?$', views.moderate_comment, name='moderate_comment'),
    url(r'^delete/(?:pk-(?P<pk>[\w\-]+)/)?$', views.delete_comment, name='delete_comment'),
]
