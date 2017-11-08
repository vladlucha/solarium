from django.conf.urls import url
from . import views
from django.contrib import admin

admin.autodiscover()

urlpatterns = [
    url(r'^all/+(?P<page_number>\d+)?$', views.all_posts, name='all_posts'),
    url(r'^create/(?P<post_id>\w+)$', views.create_post, name='create_post'),
    url(r'^save/', views.create_or_update_post, name='create_or_update_post'),
    url(r'^delete/(?P<post_id>\w+)$', views.delete_post, name='delete_post'),
]
