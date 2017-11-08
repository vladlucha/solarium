from django.conf.urls import url

from django.contrib import admin
from . import views

admin.autodiscover()

urlpatterns = [
                       url(r'^$', views.all_brands, name='brands'),
                       url(r'^create_brand/(?P<brand_id>\w+)$', views.create_brand, name='create_brand'),
                       url(r'^delete_brand/(?P<brand_id>\w+)$', views.delete_brand, name='delete_brand'),
                       url(r'^save/', views.create_or_update_brand, name='create_or_update_brand'),
                       ]
