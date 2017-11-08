from django.conf.urls import url
from . import views
from django.contrib import admin

admin.autodiscover()

urlpatterns = [
    url(r'^(?P<page_number>\d+)?$', views.shop, name='shop'),
    url(r'^(?:item-(?P<item_slug>[\w\-]+)/)?$', views.get_item, name='get_item')
]
