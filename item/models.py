from __future__ import unicode_literals

import datetime
from uuid import uuid4

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

# Create your models here.
from brand.models import Brand
from media_library.models import Media
from salarium.models_utils import format_slug
from tags.models import Tag


class Size(models.Model):
    name = models.CharField(max_length=150, unique=False, default=None, null=True)


class SizeGroup(models.Model):
    name = models.CharField(max_length=40, unique=False, default=None)
    sizes = models.ManyToManyField(Size)


class Material(models.Model):
    name = models.CharField(max_length=150, unique=True, default='', null=False)


class Color(models.Model):
    name = models.CharField(max_length=150, unique=False, default=None)
    hex = models.CharField(max_length=150, unique=False, default=None)


class ItemSizeCountMap(models.Model):
    size = models.ForeignKey(Size, default=None, on_delete=models.CASCADE, null=True, related_name="size_count")
    count = models.IntegerField(null=False, default=0)

    @property
    def current_count(self):
        return self.count - sum([o.count for o in self.orders.all()])


class Sale(models.Model):
    name = models.CharField(max_length=150, unique=False, default=None)
    date_of_start = models.DateTimeField(null=True)
    date_of_end = models.DateTimeField(null=True)
    rate = models.PositiveIntegerField(default=0, validators=[
        MaxValueValidator(100),
        MinValueValidator(0)
    ])


class ItemType(models.Model):
    name = models.CharField(max_length=150, unique=False, default=None)


class Item(models.Model):
    name = models.CharField(max_length=150, unique=False, default=None)
    slug = models.CharField(max_length=150, unique=False, default=str(uuid4))
    description = models.TextField(unique=False, default=None)
    tags = models.ManyToManyField(Tag, related_name='item_tags')
    thumbnail = models.ForeignKey(Media, default=None, null=True, on_delete=models.SET_NULL,
                                  related_name='item_thumbnail')
    gallery = models.ManyToManyField(Media, related_name='gallery')
    materials = models.ManyToManyField(Material, default=None)
    colors = models.ManyToManyField(Color)
    manufacturer_country = models.CharField(max_length=150, unique=False, default=None)
    sales = models.ManyToManyField(Sale, default=None)
    items_count = models.ManyToManyField(ItemSizeCountMap, default=None, related_name="items")
    categories = models.ManyToManyField('categories.Category', default=None, related_name="items")
    brand = models.ForeignKey(Brand, default=None, null=True, related_name="items")
    price = models.IntegerField(default=0, null=False)
    us_price = models.IntegerField(default=0, null=True)
    types = models.ManyToManyField(ItemType, default=None, related_name="items")

    @property
    def active_sale(self):
        active_sales = self.sales.filter(date_of_start__lte=datetime.datetime.now(), date_of_end__gte=datetime.datetime.now()).all()
        return max(active_sales, key=lambda x: x.rate) if len(active_sales) > 0 else None

    @property
    def item_price(self):
        rate = (self.active_sale.rate / 100) if self.active_sale else 0
        return self.price * (1 - rate)

    @property
    def item_us_price(self):
        rate = (self.active_sale.rate / 100) if self.active_sale else 0
        return self.us_price * (1 - rate)

    @staticmethod
    def save_item(**kwargs):
        gallery = kwargs.pop('gallery', [])
        materials = kwargs.pop('materials', [])
        sales = kwargs.pop('sales', [])
        categories = kwargs.pop('categories', [])
        sizes_count = kwargs.pop('sizes_count')
        item_types = kwargs.pop('types')
        tags = Tag.save_tags(kwargs.pop('tags').split(','))
        kwargs['slug'] = kwargs['name'].replace(' ', '-')
        kwargs['slug'] = format_slug(kwargs['slug'])
        new_item = Item.objects.create(**kwargs)
        new_item.brand = kwargs.pop('brand')
        for item_type in item_types:
            new_item.types.add(item_type)
        for item_gallery_image in gallery:
            if item_gallery_image:
                new_item.gallery.add(item_gallery_image)
        for material in materials:
            new_item.materials.add(material)
        for sale in sales:
            new_item.sales.add(sale)
        for category in categories:
            new_item.categories.add(category)
        for size_count in sizes_count:
            new_item_size_count = ItemSizeCountMap.objects.create(size=size_count['size'], count=size_count['count'])
            new_item.items_count.add(new_item_size_count)
        for tag in tags:
            if tag not in new_item.tags.all():
                new_item.tags.add(tag)
        new_item.save()
        return new_item

    @staticmethod
    def update_item(pk, **kwargs):
        gallery = kwargs.pop('gallery', [])
        materials = kwargs.pop('materials', [])
        sales = kwargs.pop('sales', [])
        categories = kwargs.pop('categories', [])
        sizes_count = kwargs.pop('sizes_count')
        item_types = kwargs.pop('types')
        kwargs['slug'] = kwargs['name'].replace('"', '')
        kwargs['slug'] = format_slug(kwargs['slug'])

        tags = Tag.save_tags(kwargs.pop('tags').split(','))
        Item.objects.filter(pk=pk).update(**kwargs)
        item = Item.objects.get(pk=pk)

        item.tags.clear()
        item.gallery.clear()
        item.materials.clear()
        item.items_count.clear()
        item.categories.clear()
        item.types.clear()

        item.brand = kwargs.pop('brand')

        for item_type in item_types:
            item.types.add(item_type)
        for item_gallery_image in gallery:
            item.gallery.add(item_gallery_image)
        for material in materials:
            item.materials.add(material)
        for sale in sales:
            item.sales.add(sale)
        for category in categories:
            item.categories.add(category)
        for size_count in sizes_count:
            new_item_size_count = ItemSizeCountMap.objects.create(size=size_count['size'], count=size_count['count'])
            item.items_count.add(new_item_size_count)
        for tag in tags:
            item.tags.add(tag)
        item.save()
        return item

    @staticmethod
    def filter_by_brands(query, filter_data):
        query = query.filter(brand__pk__in=filter_data)
        return query

    @staticmethod
    def filter_by_categories(query, filter_data):
        query = query.filter(categories__pk__in=filter_data)
        return query

    @staticmethod
    def filter_by_max_price(query, filter_data):
        query = query.filter(price__lte=filter_data)
        return query

    @staticmethod
    def filter_by_min_price(query, filter_data):
        query = query.filter(price__gte=filter_data)
        return query

    @staticmethod
    def filter_by_sizes(query, filter_data):
        query = query.filter(items_count__size__pk__in=filter_data)
        return query

    @staticmethod
    def filter_by_types(query, filter_data):
        query = query.filter(types__pk__in=filter_data)
        return query
