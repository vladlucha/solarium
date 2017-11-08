from django.conf.urls import url
from django.contrib import admin
from . import views

admin.autodiscover()

urlpatterns = [
   url(r'^$', views.get_orders, name='basket'),
   url(r'^step/(?:(?P<transaction_pk>[\w\-]+)/)?/?step=(?:(?P<step>[\w\-]+)/)?', views.render_step, name='render_step'),
   url(r'^order/create/$', views.create_order, name='create_order'),
   url(r'^transaction/(?:transaction_uuid-(?P<transaction_uuid>[\w\-]+)/)?$', views.get_transaction, name='get_transaction'),
   url(r'^modify/(?:transaction_uuid-(?P<transaction_uuid>[\w\-]+)/)?$', views.modify_transaction, name='modify_transaction'),
   url(r'^order/delete/(?:order_uuid-(?P<order_uuid>[\w\-]+)/)?$', views.delete_order, name='delete_order'),
   url(r'^create_transaction', views.create_transaction, name='create_transaction'),
   url(r'^orders/(?:(?P<order_status>[\w\-]+)/)?$', views.admin_orders, name='admin_orders'),
   url(r'^orders/change_count/(?:order_uuid-(?P<order_uuid>[\w\-]+)/)?', views.change_order_count, name='change_count'),
   url(r'^promocode/$', views.check_promocode, name='check_promocode'),
   url(r'^payment/(?:(?P<payment_status>[\w\-]+)/)?$', views.change_payment_status, name='change_payment_status')
]
