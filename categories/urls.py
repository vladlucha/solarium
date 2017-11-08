from django.conf.urls import url
from . import views
from django.contrib import admin

admin.autodiscover()

urlpatterns = [
    url(r'^$', views.categories, name='categories'),
    url(r'^create/', views.create, name='create_category'),
    url(r'^update/(?P<category_pk>[0-9]+)/$', views.update_category, name='update_category'),
    url(r'^edit/(?P<category_pk>[0-9]+)/$', views.create_category_view, name='edit_category'),
]
