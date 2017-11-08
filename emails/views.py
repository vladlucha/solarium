# -*- coding: utf-8 -*-
from django.shortcuts import render, redirect

from item.models import Item
from salarium.tasks import send_email_template_task

# Create your views here.
from customer.models import Customer
from emails.models import EmailTemplate
from salarium.utils import page_render, staff_only, set_request_session_alert


@staff_only
def get_templates(request):
    return page_render(request, 'admin_panel/main_page_admin_panel.html',
                       {'email_templates': 'active',
                        'current_content_page': 'admin_panel/emails/email_templates_list.html',
                        'templates': EmailTemplate.objects.all()})


@staff_only
def add_email_template(request, template_pk=None):
    if request.method == 'POST':
        data = {
            'body': request.POST.get('body', ''),
            'subject': request.POST.get('subject', ''),
            'name': request.POST.get('name', '')
        }
        if request.POST.get('pk', '') != '' and EmailTemplate.objects.filter(pk=int(request.POST.get('pk'))).exists():
            EmailTemplate.objects.filter(pk=int(request.POST.get('pk', '-1'))).update(**data)
        else:
            EmailTemplate.objects.create(**data)
        return redirect('email_templates')

    template = EmailTemplate.objects.filter(pk=int(template_pk)).first() if template_pk else None
    return page_render(request, 'admin_panel/main_page_admin_panel.html',
                       {'email_templates': 'active',
                        'current_content_page': 'admin_panel/emails/new_email_template.html',
                        'email_template': template, 'items': Item.objects.all()})


@staff_only
def delete_template(request, template_pk):
    alert_message = 'Произошла ошибка'
    if request.method == 'POST':
        template = EmailTemplate.objects.filter(pk=template_pk)
        if template.exists():
            template.delete()
            alert_message = 'Шаблон успешно удален'
    set_request_session_alert(request, alert_message, 'notice')
    return redirect('email_templates')


def get_delivers(request):
    return page_render(request, 'admin_panel/main_page_admin_panel.html',
                       {'email_mailing': 'active', 'templates': EmailTemplate.objects.all(),
                        'current_content_page': 'admin_panel/emails/email_delivery.html'})


@staff_only
def send_emails(request):
    if request.method == "POST":
        recipients = Customer.objects.filter(include_in_email_delivery=True).all()
        for rcp in recipients:
            send_email_template_task.delay(request.POST.get('template_pk'), to=rcp.email)
    return redirect('email_mailing')
