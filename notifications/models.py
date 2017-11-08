from __future__ import unicode_literals

from uuid import uuid4

from django.db import models

# Create your models here.
from customer.models import Customer
from salarium.enums import NotificationsStatus, NotificationsType, NotificationsScope


class Notification(models.Model):
    uuid = models.CharField(max_length=150, unique=False, default=str(uuid4()))
    type = models.CharField(max_length=150, unique=False, default=None, choices=NotificationsType.choices())
    status = models.CharField(max_length=150, unique=False, default=NotificationsStatus.Actual.value, choices=NotificationsStatus.choices())
    scope = models.CharField(max_length=150, unique=False, default=NotificationsScope.System.value, choices=NotificationsScope.choices())
    receiver = models.ForeignKey(Customer, default=None, null=True)
    description = models.TextField(default='')
    entity_pk = models.IntegerField(null=True, default=None)
    date_of_creation = models.DateTimeField(auto_now_add=True)

    @classmethod
    def create_notification(self, **kwargs):
        kwargs['status'] = NotificationsStatus.Actual.value
        new_notification = self.objects.create(**kwargs)
        new_notification.save()
        return new_notification

    def update_notification(self, **kwargs):
        if 'status' not in kwargs:
            kwargs['status'] = NotificationsStatus.Actual.value
        self.__dict__.update(**kwargs)
        self.save()
        return self

    def set_viewed(self):
        self.status = NotificationsStatus.Viewed.value
        self.save()
        return self
