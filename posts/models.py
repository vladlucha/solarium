from __future__ import unicode_literals

import uuid

from django.db import models
from media_library.models import Media
from customer.models import Customer


# Create your models here.
from salarium.enums import EntityStatus
from salarium.models_utils import format_slug
from tags.models import Tag


class Post(models.Model):
    title = models.CharField(max_length=150, unique=False, default=None)
    body = models.TextField(unique=False, default=None)
    formatted_body = models.TextField(unique=False, default=None)
    tags = models.ManyToManyField(Tag, related_name='tags')
    thumbnail = models.ForeignKey(Media, default=None, null=True, on_delete=models.SET_NULL)
    excerpt = models.CharField(max_length=255, unique=False, default=None)
    slug = models.CharField(max_length=255, unique=False, default=str(uuid.uuid4()))
    date_of_creation = models.DateTimeField(auto_now_add=True)
    date_of_last_changes = models.DateTimeField(null=True)
    status = models.CharField(max_length=100, default=EntityStatus.Pending.value, choices=EntityStatus.choices())
    author = models.ForeignKey(Customer, on_delete=models.CASCADE, default=None, null=True)
    comments = models.ManyToManyField('comments.Comment', related_name='comments')

    @staticmethod
    def save_post(**kwargs):
        tags = Tag.save_tags(kwargs.pop('tags').split(','))

        kwargs['slug'] = kwargs['title'].replace(' ', '_')
        kwargs['slug'] = format_slug(kwargs['slug'])
        new_post = Post.objects.create(**kwargs)

        for tag in tags:
            if tag not in new_post.tags.all():
                new_post.tags.add(tag)
        new_post.save()
        return new_post

    @staticmethod
    def update_post(pk, **kwargs):
        tags = Tag.save_tags(kwargs.pop('tags').split(','))
        kwargs['slug'] = kwargs['title'].replace(' ', '_')
        kwargs['slug'] = format_slug(kwargs['slug'])
        Post.objects.filter(pk=pk).update(**kwargs)
        new_post = Post.objects.filter(pk=pk).first()
        new_post.tags.clear()

        for tag in tags:
            if tag not in new_post.tags.all():
                new_post.tags.add(tag)
        new_post.save()
        return new_post

    @staticmethod
    def get_post_by_property(**kwargs):
        return Post.objects.filter(**kwargs).first()

    @staticmethod
    def get_all_posts():
        return Post.objects.all()