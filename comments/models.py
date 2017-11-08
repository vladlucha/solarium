from __future__ import unicode_literals

from django.db import models

# Create your models here.
from customer.models import Customer
from posts.models import Post
from salarium.enums import EntityStatus


class Comment(models.Model):
    body = models.TextField(unique=False, default=None)
    date_of_creation = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=100, default=EntityStatus.Pending.value, choices=EntityStatus.choices())
    author = models.ForeignKey(Customer, on_delete=models.CASCADE, default=None, null=True)
    name = models.CharField(max_length=100,  default=None, null=True)
    email = models.EmailField(max_length=100,  default=None, null=True)

    @staticmethod
    def save_comment(post_pk, **kwargs):
        if not kwargs['author'].is_authenticated:
            kwargs.pop('author')

        comment = Comment.objects.create(**kwargs)
        comment.save()

        post = Post.objects.filter(pk=post_pk).first()
        post.comments.add(comment)
        post.save()

        return comment

    @staticmethod
    def update_comment(pk, **kwargs):
        Comment.objects.filter(pk=pk).update(**kwargs)
        comment = Comment.objects.filter(pk=pk).first()
        return comment
