from datetime import datetime, timedelta

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.template import Template
from django.template.defaultfilters import register
from django.template.loader import get_template
from django.views.decorators.csrf import csrf_exempt

from django.template import Context
from django.core.mail import EmailMessage
from django.utils.encoding import smart_text

import vk_api
from basket.models import Order
from customer.models import UserActivity, Customer
from salarium import settings

login_context_data = {'force_login_form': False, 'sign_up_email': '', 'sign_up_password': '', 'sign_up_error': None,
                      'remember_me': False, 'sign_in_email': '', 'sign_in_password': '', 'sign_in_error': None}


def page_render(request, template, context=None):
    # type: (object, object, object) -> object
    context = {} if context is None else context
    if 'alert_message' in request.session:
        context.update({'alert_message': request.session.pop('alert_message'),
                        'alert_type': request.session.pop('alert_type')})

    context.update({'template': template})
    context.update(_build_login_context(request))
    context['basket_items_count'] = Order.objects.filter(purchaser__pk=request.user.pk, transaction__isnull=True).count()
    return render(request, 'basic_templates/base_template.html', context)


def _build_login_context(request):
    data = {}
    for key, default_value in login_context_data.items():
        data[key] = request.session.pop(key, default_value)
    return data


def set_request_session_alert(request, alert_message, alert_type):
    request.session['alert_message'] = alert_message
    request.session['alert_type'] = alert_type


def base_admin_panel_return(request, data, alert_type='info', alert_message=None):
    return page_render(request, 'admin_panel/main_page_admin_panel.html',
                       {'categories_is_active': 'active',
                        'current_content_page': 'admin_panel/categories/categories.html',
                        'categories': data,
                        'alert_type': alert_type,
                        'alert_message': alert_message
                        })


def get_page_data(objects, page, items_per_page=10):
    paginator = Paginator(objects, items_per_page)

    try:
        page = int(page)
    except ValueError:
        page = 1

    if page == 0:
        page += 1

    try:
        objects = paginator.page(page)
    except PageNotAnInteger:
        objects = paginator.page(1)
        page = 1
    except EmptyPage:
        objects = paginator.page(paginator.num_pages)
        page = paginator.num_pages
    return page, objects, paginator.num_pages + 1


def staff_only(f):
    @csrf_exempt
    def wrap(request, *args, **kwargs):
        # this check the session if userid key exist, if not it will redirect to login page
        if not request.user.is_authenticated() or not request.user.is_team:
            return HttpResponseRedirect("/")
        elif 'view_type' not in request.session:
            request.session.view_type = 'list'
        return f(request, *args, **kwargs)

    wrap.__doc__ = f.__doc__
    wrap.__name__ = f.__name__
    return wrap


def format_time(td_object):
    seconds = int(td_object.total_seconds())
    periods = [
        ('year ', 60 * 60 * 24 * 365),
        ('month ', 60 * 60 * 24 * 30),
        ('day ', 60 * 60 * 24),
        ('h', 60 * 60),
        ('m', 60),
        ('s', 1)
    ]

    strings = []
    for period_name, period_seconds in periods:
        if seconds > period_seconds:
            period_value, seconds = divmod(seconds, period_seconds)
            if period_value == 1:
                strings.append("%s%s " % (period_value, period_name))
            else:
                strings.append("%s%s " % (period_value, period_name))

    return "".join(strings)


def format_form_data(model, form_data):
    fields_names = [field.name for field in model._meta.fields]
    result = {}
    for field_name in fields_names:
        values = [field['value'] for field in form_data if field['name'] == field_name]
        value = values[0] if len(values) == 1 else values

        if len(values) > 0:
            result[field_name] = value
    return result


@register.filter(name='post_counter')
def post_counter(value):
    value %= 3
    return 3 if value == 0 else value


@register.filter(name='get')
def get(value):
    return value if value != 'None' and value else ''


@register.filter(name='transaction_items_count')
def transaction_items_count(transaction):
    count = sum([o.count for o in transaction.orders.all()])
    return count or 0


@register.filter(name='transaction_total_price')
def transaction_total_price(transaction):
    count = sum([o.item.item_price * o.count for o in transaction.orders.all()])
    return count or 0


def get_page_number(number, route=None):
    try:
        number = int(number)
    except Exception as ex:
        if route:
            return redirect(route, page_number=1)
        number = 1
    return number


def parse_int(value, default=None):
    try:
        value = int(value)
    except Exception as ex:
        value = default
    return value


@register.filter(name='get_from_dict')
def get_from_dict(dict, key):
    return dict.get(key, None)


@register.simple_tag(name='online_users')
def online_users(num=None):
    five_minutes = datetime.now() - timedelta(minutes=5)
    sql_datetime = datetime.strftime(five_minutes, '%Y-%m-%d %H:%M:%S')
    users = UserActivity.objects.filter(last_activity_date__gte=sql_datetime, user__is_active__exact=1).order_by(
        '-last_activity_date')
    if num:
        users = users[:num]

    return get_template('admin_panel/settings/online_users.html').render(Context({'online_users': users}))


@register.simple_tag(name='online_admin')
def online_admin():
    five_minutes = datetime.now() - timedelta(minutes=5)
    sql_datetime = datetime.strftime(five_minutes, '%Y-%m-%d %H:%M:%S')
    admin = UserActivity.objects\
        .filter(last_activity_date__gte=sql_datetime, user__is_active__exact=1, user__is_admin__exact=1)\
        .first()
    if admin:
        return admin.user
    return None


@register.simple_tag(name='admin_user')
def admin_user():
    admin = Customer.objects.filter(is_admin=True).first()
    return admin


@register.simple_tag(name='post_delivery_cost')
def post_delivery_cost(total_price):
    return '{:10.2f} руб.'.format((total_price * 0.02) + 3.5)


def VK_session():
    vk_session = vk_api.VkApi(settings.VK_ADMIN_EMAIL, settings.VK_ADMIN_PASSWORD)
    try:
        vk_session.auth()
        return vk_session
    except vk_api.AuthError as error_msg:
        print(error_msg)
        return None


def send_email(template, subject, to, context=None, from_email=None):
    """
    Send email
    :param template: template name in templates folder
    :param subject: template subject
    :param to: to (list or one item) email
    :param context: context dict for render template
    :param from_email: from email
    """

    if template:
        if not isinstance(to, list):
            to = [to]
        message = Template(template).render(Context(context))
        subject = subject or 'Subject'
        msg = EmailMessage(smart_text(subject), message, to=to, from_email=from_email)
        msg.content_subtype = 'html'
        msg.send()
