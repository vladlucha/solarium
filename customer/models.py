from __future__ import unicode_literals

from datetime import datetime, timedelta

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.core.validators import RegexValidator
from django.db import models
from random import randint

from media_library.models import Media
from lazysignup.utils import is_lazy_user


class CustomerManager(BaseUserManager):
    def create_user(self, email, password):
        username = email.split('@')[0]
        if Customer.objects.filter(username=username).exists():
            username += str(randint(0, 1001))
        user = self.model(email=email,
                          username=username)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, username):
        user = self.model.objects.filter(email=email)
        if not user.exists():
            user = self.model(email=email,
                              username=username,
                              is_team=True,
                              is_admin=True)
            user.set_password(password)
            user.save()
        return user

    def create_moderator(self, email, password, username):
        user = self.model(email=email,
                          username=username,
                          is_team=True)
        user.set_password(password)
        user.save()
        return user


class Customer(AbstractBaseUser):
    username = models.CharField(max_length=254, unique=True)
    thumbnail = models.ForeignKey(Media, default=None, null=True, on_delete=models.SET_NULL, related_name='user_thumbnail')
    name = models.CharField(max_length=254, unique=False, null=True, default=None)
    surname = models.CharField(max_length=254, unique=False, null=True, default=None)
    patronymic = models.CharField(max_length=254, unique=False, null=True, default=None)
    email = models.EmailField(blank=True, unique=True)
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number invalid.")
    phone_number = models.CharField(validators=[phone_regex], blank=True, max_length=15, null=True, default=None)
    address = models.CharField(max_length=254, unique=False, null=True, default=None)
    house = models.CharField(max_length=254, unique=False, null=True, default=None)
    housing_number = models.CharField(max_length=254, unique=False, null=True, default=None)
    flat_number = models.CharField(max_length=254, unique=False, null=True, default=None)
    post_index = models.CharField(max_length=254, unique=False, null=True, default=None)
    is_team = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    include_in_email_delivery = models.BooleanField(default=False)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    objects = CustomerManager()

    def is_online(self):
        five_minutes = datetime.now() - timedelta(minutes=5)
        sql_datetime = datetime.strftime(five_minutes, '%Y-%m-%d %H:%M:%S')
        activity = UserActivity.objects.filter(last_activity_date__gte=sql_datetime, user__pk=self.pk) \
            .first()
        return activity is not None

    def get_full_name(self):
        # The user is identified by their email address
        return self.email

    def get_short_name(self):
        # The user is identified by their email address
        return self.email

    def __unicode__(self):
        return self.email

    def update(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        return self

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @staticmethod
    def get_all_customers():
        return [u for u in Customer.objects.all() if not is_lazy_user(u)]

    @staticmethod
    def is_email_unique(email):
        return Customer.objects.filter(email=email).count() == 0

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin

    @property
    def messages(self):
        return reversed(self.sent_messages.order_by('-timestamp') | self.received_messages.order_by('-timestamp'))


class UserActivity(models.Model):
    last_activity_ip = models.GenericIPAddressField()
    last_activity_date = models.DateTimeField(default=datetime(1950, 1, 1))
    user = models.OneToOneField(Customer, primary_key=True)
