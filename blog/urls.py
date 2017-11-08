from django.conf.urls import url

from django.contrib import admin
from . import views

admin.autodiscover()

urlpatterns = [
    url(r'^$', views.posts, name='blog'),
    url(r'^post/(?:slug-(?P<post_slug>[\w\-]+)/)?$', views.get_post, name='get_post'),
    url(r'^post/(?:tag-(?P<tag>[\w\-]+)/)?$', views.get_posts_by_tag, name='get_posts_by_tag'),
    url(r'^post/(?:category-(?P<category>[\w\-]+)/)?$', views.get_posts_by_category, name='get_posts_by_category'),
    url(r'^post/(?:page-(?P<page>[\w\-]+)/)?$', views.get_posts_by_page, name='get_posts_by_page')
]
