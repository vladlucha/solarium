# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2017-05-17 01:01
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('media_library', '0001_initial'),
        ('categories', '0001_initial'),
        ('tags', '0001_initial'),
        ('brand', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Color',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default=None, max_length=150)),
                ('hex', models.CharField(default=None, max_length=150)),
            ],
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default=None, max_length=150)),
                ('slug', models.CharField(default='<function uuid4 at 0x7fc64b6fc048>', max_length=150)),
                ('description', models.TextField(default=None)),
                ('manufacturer_country', models.CharField(default=None, max_length=150)),
                ('price', models.IntegerField(default=0)),
                ('us_price', models.IntegerField(default=0, null=True)),
                ('brand', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='items', to='brand.Brand')),
                ('categories', models.ManyToManyField(default=None, related_name='items', to='categories.Category')),
                ('colors', models.ManyToManyField(to='item.Color')),
                ('gallery', models.ManyToManyField(related_name='gallery', to='media_library.Media')),
            ],
        ),
        migrations.CreateModel(
            name='ItemSizeCountMap',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('count', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='ItemType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default=None, max_length=150)),
            ],
        ),
        migrations.CreateModel(
            name='Material',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='', max_length=150, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Sale',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default=None, max_length=150)),
                ('date_of_start', models.DateTimeField(null=True)),
                ('date_of_end', models.DateTimeField(null=True)),
                ('rate', models.PositiveIntegerField(default=0, validators=[django.core.validators.MaxValueValidator(100), django.core.validators.MinValueValidator(0)])),
            ],
        ),
        migrations.CreateModel(
            name='Size',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default=None, max_length=150, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='SizeGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default=None, max_length=40)),
                ('sizes', models.ManyToManyField(to='item.Size')),
            ],
        ),
        migrations.AddField(
            model_name='itemsizecountmap',
            name='size',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='size_count', to='item.Size'),
        ),
        migrations.AddField(
            model_name='item',
            name='items_count',
            field=models.ManyToManyField(default=None, related_name='items', to='item.ItemSizeCountMap'),
        ),
        migrations.AddField(
            model_name='item',
            name='materials',
            field=models.ManyToManyField(default=None, to='item.Material'),
        ),
        migrations.AddField(
            model_name='item',
            name='sales',
            field=models.ManyToManyField(default=None, to='item.Sale'),
        ),
        migrations.AddField(
            model_name='item',
            name='tags',
            field=models.ManyToManyField(related_name='item_tags', to='tags.Tag'),
        ),
        migrations.AddField(
            model_name='item',
            name='thumbnail',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='item_thumbnail', to='media_library.Media'),
        ),
        migrations.AddField(
            model_name='item',
            name='types',
            field=models.ManyToManyField(default=None, related_name='items', to='item.ItemType'),
        ),
    ]