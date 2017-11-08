from __future__ import unicode_literals

from uuid import uuid4

from django.db import models
from media_library.models import Media
# Create your models here.
from salarium.enums import EntityStatus


class Brand(models.Model):
    name = models.CharField(max_length=150, unique=False, default=None)
    slug = models.CharField(max_length=150, unique=False, default=str(uuid4()))
    description = models.TextField(unique=False, default=None)
    thumbnail = models.ForeignKey(Media, default=None, null=True, on_delete=models.SET_NULL, related_name='thumbnail')
    banner = models.ForeignKey(Media, default=None, null=True, on_delete=models.SET_NULL, related_name='banner')
    country = models.CharField(max_length=150, unique=False, default=None)
    status = models.CharField(max_length=100, default=EntityStatus.Pending.value, choices=EntityStatus.choices())

    @staticmethod
    def save_brand(**kwargs):
        kwargs['slug'] = kwargs.get('name').replace(' ', '_')
        new_brand = Brand.objects.create(**kwargs)
        new_brand.save()
        return new_brand

    @staticmethod
    def update_brand(pk, **kwargs):
        kwargs['slug'] = kwargs.get('name').replace(' ', '_')
        brand = Brand.objects.filter(pk=pk).update(**kwargs)
        return brand

    @staticmethod
    def get_brand_by_property(**kwargs):
        return Brand.objects.filter(**kwargs).first()

    @staticmethod
    def get_all_brands():
        return Brand.objects.all()
