from __future__ import unicode_literals

from django.db import models

# Create your models here.
from django.template.loader import render_to_string


class EmailTemplate(models.Model):
    name = models.CharField(unique=True, null=False, max_length=128)
    subject = models.CharField(unique=False, null=False, max_length=128, default='subject')
    body = models.TextField(unique=False, default=None)
    date_of_creation = models.DateTimeField(auto_now_add=True)

    @property
    def email_preview(self):
        return render_to_string('admin_panel/emails/email_preview.html', {'email_template': self})


class EmailRecipients(models.Model):
    email_address = models.EmailField(unique=True, null=False)
    is_active = models.BooleanField(default=False)
