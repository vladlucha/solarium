from django.conf.urls import url
from django.contrib import admin
from . import views
admin.autodiscover()

urlpatterns = [
    url(r'^$', views.media_library, name='media_library_all'),
    url(r'^images/', views.media_library_images, name='media_library_images'),
    url(r'^library/images/+(?P<page_number>\d+)?$', views.load_more_items, name='load_images'),
    url(r'^album/+(?P<album_pk>\d+)?$', views.load_album_images, name='load_album_images'),
    url(r'^videos/', views.media_library_video, name='media_library_video'),
    url(r'^modal_library', views.get_modal_media_library, name='get_modal_library'),
    url(r'^upload', views.upload_media, name='upload_media'),
    url(r'^delete', views.delete_media, name='delete_media'),
    url(r'^get_image', views.get_image_custom_size, name='get_image_custom_size'),
    url(r'^sync', views.synchronize_media, name='synchronize_media')
]
