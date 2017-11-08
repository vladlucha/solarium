from django.conf.urls import url, include
from . import views

from django.contrib import admin
admin.autodiscover()

urlpatterns = [
    url(r'^$', views.index, name='authentication'),
]