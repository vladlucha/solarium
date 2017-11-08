from django.conf.urls import url
from . import views
from django.contrib import admin

admin.autodiscover()

urlpatterns = [
    url(r'^shop_view_settings/', views.shop_view_settings, name='shop_view_settings'),
    url(r'^update_shop_view_settings/', views.update_shop_view_settings, name='update_shop_view_settings'),
]
