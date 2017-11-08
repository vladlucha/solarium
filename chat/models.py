from __future__ import unicode_literals
from django.db import models
from customer.models import Customer


class Message(models.Model):
    author = models.ForeignKey(Customer, related_name='sent_messages')
    recipient = models.ForeignKey(Customer, null=True, default=None, related_name='received_messages')
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

