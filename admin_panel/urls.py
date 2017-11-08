from django.conf.urls import include, url

from django.contrib import admin
from . import views

admin.autodiscover()

urlpatterns = [
   url(r'^$', views.dashboard, name='admin_panel'),
   url(r'^more_notifications', views.get_more_notifications, name='get_more_notifications'),
   url(r'^user_list/', views.user_list, name='user_list'),
   url(r'^toggle_rss/(?P<user_pk>[0-9]+)/$', views.toggle_rss, name='toggle_rss'),
   url(r'^change_availability/(?P<user_pk>[0-9]+)/$', views.change_availability, name='change_availability'),
   url(r'^messages', views.user_messages, name='user_messages'),
   url(r'^chat/(?P<user_pk>[0-9]+)', views.chat_with_user, name='chat_with_user'),
]
