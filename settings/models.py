from __future__ import unicode_literals
from django.db import models

from media_library.models import Media


class Settings(models.Model):
    title = models.CharField(max_length=255, unique=True, null=True, default=None)
    description = models.TextField(unique=False, null=True, default=None)
    thumbnail = models.ForeignKey(Media, unique=False, null=True, default=None)
    count_of_jobs = models.IntegerField(default=0, unique=False, null=False)

    @property
    def sync_in_process(self):
        return self.count_of_jobs > 0
