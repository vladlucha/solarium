from __future__ import unicode_literals

from django.db import models

# Create your models here.
from media_library.models import Media


class SliderText(models.Model):
    html = models.TextField(unique=False, null=True, default=None)
    uuid = models.CharField(max_length=10, null=False, default='-')


class Slide(models.Model):
    thumbnail = models.ForeignKey(Media, unique=False, null=True, default=None)
    title = models.CharField(max_length=150, unique=False, default=None)
    href = models.CharField(max_length=450, unique=False, default=None, null=True)
    description = models.TextField(unique=False, null=True, default=None)
    order = models.IntegerField(unique=False, null=False, default=0)
    is_active = models.BooleanField(unique=False, null=False, default=True)

    def reorder_slides(self):
        updated_orders = [int(self.order)]
        slides = Slide.objects.filter(order__gte=self.order)
        for slide in slides:
            if int(slide.order) in updated_orders and slide.pk != self.pk:
                slide.order += 1
                updated_orders.append(int(slide.order))
                slide.save()
