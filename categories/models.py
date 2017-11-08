from __future__ import unicode_literals
from django.db import models

from media_library.models import Media


class Category(models.Model):
    name = models.CharField(max_length=255, unique=True, null=False)
    description = models.TextField(unique=False, null=True, default=None)
    thumbnail = models.ForeignKey(Media, unique=False, null=True, default=None)

    @staticmethod
    def create_category(name):
        new_category = Category.objects.create(name=name)
        new_category.save()
        return new_category

    @staticmethod
    def get_all_categories():
        return Category.objects.all()

    @staticmethod
    def get_category_by_name(name):
        return Category.objects.filter(name=name)
