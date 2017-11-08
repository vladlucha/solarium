from django.conf.urls import url
from . import views
from django.contrib import admin

admin.autodiscover()

urlpatterns = [
    url(r'^all/+(?P<page_number>\d+)?$', views.all_items, name='items'),
    url(r'^create_item/(?P<item_id>\w+)/$', views.create_item, name='create_item'),
    url(r'^items_settings', views.items_settings, name='items_settings'),
    url(r'^sales/+(?P<page_number>\d+)?$', views.sales, name='sales'),
    url(r'^create_size_group/', views.create_size_group, name='create_size_group'),
    url(r'^delete_size_group/', views.delete_size_group, name='delete_size_group'),
    url(r'^update_size_group/', views.update_size_group, name='update_size_group'),
    url(r'^create_size/(?P<size_group_id>\w+)/$', views.create_size, name='create_size'),
    url(r'^delete_size/', views.delete_size, name='delete_size'),
    url(r'^promocodes', views.promocodes, name='promocodes'),
    url(r'^create_promocode', views.create_promocode, name='create_promocode'),
    url(r'^update_promocode/(?P<promocode_id>\w+)', views.update_promocode, name='update_promocode'),
    url(r'^delete_promocode/(?P<promocode_id>\w+)', views.delete_promocode, name='delete_promocode'),
    url(r'^create_material/', views.create_material, name='create_material'),
    url(r'^delete_material/', views.delete_material, name='delete_material'),
    url(r'^update_material/', views.update_material, name='update_material'),
    url(r'^item_types/', views.item_types, name='item_types'),
    url(r'^create_item_type/', views.create_item_type, name='create_item_type'),
    url(r'^delete_item_type/', views.delete_item_type, name='delete_item_type'),
    url(r'^update_item_type/', views.update_item_type, name='update_item_type'),
    url(r'^create_sale/', views.create_sale, name='create_sale'),
    url(r'^delete_sale/', views.delete_sale, name='delete_sale'),
    url(r'^create_or_update_item/', views.create_or_update_item, name='create_or_update_item')
]
