# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2017-05-17 01:01
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('media_library', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Settings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(default=None, max_length=255, null=True, unique=True)),
                ('description', models.TextField(default=None, null=True)),
                ('count_of_jobs', models.IntegerField(default=0)),
                ('thumbnail', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='media_library.Media')),
            ],
        ),
    ]
