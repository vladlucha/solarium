from django.conf.urls import url
from . import views
from django.contrib import admin

admin.autodiscover()

urlpatterns = [
    url(r'templates/', views.get_templates, name='email_templates'),
    url(r'delete/(?P<template_pk>[0-9]+)', views.delete_template, name='delete_template'),
    url(r'new_template/', views.add_email_template, name='add_email_template'),
    url(r'edit/(?P<template_pk>[0-9]+)', views.add_email_template, name='edit_email_template'),
    url(r'mailing/', views.get_delivers, name='email_mailing'),
    url(r'send/', views.send_emails, name='send_emails'),
]
