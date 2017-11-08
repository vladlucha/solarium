#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from customer.models import Customer
from customer.backends import CustomerAuthBackend
from django.contrib.auth import login, logout
from django.core.validators import validate_email
from django import forms

# Create your views here.
from salarium.tasks import send_email_task
from salarium.utils import page_render


def index(request):
    if request.user.is_authenticated():
        return redirect('/')
    else:
        return page_render(request, 'site/auth.html', {'sign_in': 'active'})


def process_lazy_user(request, lazy_user):
    lazy_messages = lazy_user.messages
    user = request.user

    for message in lazy_messages:
        if message.author.pk == lazy_user.pk:
            message.author = user
        elif message.recipient.pk == lazy_user.pk:
            message.recipient = user
        message.save()

    lazy_user.delete()


def sign_in(request):
    if request.method == 'POST':
        request.session['sign_in_email'] = email = request.POST.get('email')
        request.session['sign_in_password'] = password = request.POST.get('password')
        request.session['remember_me'] = remember_me = request.POST.get('remember_me')
        try:
            validate_email(email)
        except forms.ValidationError as e:
            request.session['sign_in_error'] = 'Неправильный e-mail'
            request.session['force_login_form'] = True
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        lazy_user = request.user

        user = CustomerAuthBackend.authenticate(email=email, password=password)
        if user is not None and user.is_active:
            process_lazy_user(request, lazy_user)
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user)
            request.session['include_in_email_delivery'] = user.include_in_email_delivery
            if not remember_me:
                request.session.set_expiry(0)

        elif user is not None and not user.is_active:
            request.session['sign_in_error'] = 'Ваш аккаунт заблокирован.'
        else:
            request.session['sign_in_error'] = 'Неправильный e-mail или пароль'

        request.session['force_login_form'] = request.session.get('sign_in_error', None) is not None
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    return redirect('/')


def sign_up(request):
    if request.method == 'POST':
        request.session['sign_up_email'] = email = request.POST.get('email')
        request.session['sign_up_password'] = password = request.POST.get('password')
        request.session['remember_me'] = remember_me = request.POST.get('remember_me')
        if Customer.is_email_unique(email):
            try:
                validate_email(email)
                lazy_user = request.user

                user = Customer.objects.create_user(email=email, password=password)
                new_user = CustomerAuthBackend.authenticate(email=user.email, password=password)
                process_lazy_user(request, lazy_user)

                send_email_task.delay('Хаюхай, с вами ивансукагай, вы зарегались, все ок, ваш пароль: {}'.format(str(password)),
                                      'РЭГИСТРАЦЫЯ', [email], 'mail@salarium.by')

                new_user.backend = 'django.contrib.auth.backends.ModelBackend'
                login(request, new_user)
                if not remember_me:
                    request.session.set_expiry(0)

            except forms.ValidationError as e:
                request.session['sign_up_error'] = str(e.message)
        else:
            request.session['sign_up_error'] = "Пользователь с таким e-mail уже существует"

        request.session['force_login_form'] = request.session.get('sign_up_error', None) is not None
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    return redirect('/')


def sign_out(request):
    if request.user.is_authenticated():
        logout(request)
    return redirect('/')
