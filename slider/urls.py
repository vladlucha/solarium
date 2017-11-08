from django.conf.urls import url
from . import views
from django.contrib import admin

admin.autodiscover()

urlpatterns = [
    url(r'^$', views.all_sliders, name='sliders'),
    url(r'^create_slider/(?P<slider_id>\w+)/$', views.create_slider, name='create_slider'),
    url(r'^create_or_update_slide/', views.create_or_update_slide, name='create_or_update_slide')
]
