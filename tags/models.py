from __future__ import unicode_literals

from django.db import models


# Create your models here.
class Tag(models.Model):
    tag_text = models.CharField(max_length=150, unique=False, default=None)

    @staticmethod
    def save_tag(tag_text):
        new_tag = Tag.objects.create(tag_text=tag_text)
        new_tag.save()
        return new_tag

    @staticmethod
    def save_tags(tags):
        new_tags = []
        for tag in tags:
            tag = tag.strip()
            if not Tag.objects.filter(tag_text=tag).exists():
                tag = Tag.save_tag(tag)
            else:
                tag = Tag.objects.filter(tag_text=tag).first()
            new_tags.append(tag)
        return new_tags

    @staticmethod
    def get_all_tags():
        return Tag.objects.all()