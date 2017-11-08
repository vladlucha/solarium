from django.conf.urls import url
from . import views
from django.contrib import admin

admin.autodiscover()

urlpatterns = [
    url(r'^$', views.get_profile, name='profile'),
    url(r'edit/', views.save_profile, name='save_profile'),
    url(r'messages/', views.get_user_messages, name='messages'),
    url(r'orders/+(?P<page_number>\d+)?', views.get_user_orders, name='orders'),
    url(r'change_thumbnail', views.change_thumbnail, name='change_thumbnail'),
]
