from datetime import datetime

from django.db.models import Q
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.utils import timezone

from customer.models import Customer
from notifications.models import Notification
from salarium.enums import NotificationsType, NotificationsStatus
from salarium.utils import page_render, get_page_data, format_time
from salarium.utils import staff_only


# Create your views here.
@staff_only
def dashboard(request):
    request.session['notification_page'] = 0
    new_comments_count = Notification.objects.filter(type=NotificationsType.CommentAdded.value, status=NotificationsStatus.Actual.value).count()
    new_orders_count = Notification.objects.filter(type=NotificationsType.TransactionCreated.value, status=NotificationsStatus.Actual.value).count()
    page, notifications, number_pages = get_notifications(request)
    return page_render(request, 'admin_panel/main_page_admin_panel.html',
                       {'dashboard': 'active',
                        'current_content_page': 'admin_panel/dashboard/statistic.html',
                        'new_comments_count': new_comments_count,
                        'new_orders_count': new_orders_count,
                        'notifications': notifications,
                        'order_statuses': NotificationsType,
                        'has_more': number_pages > page + 1})


def get_more_notifications(request):
    page, notifications, number_pages = get_notifications(request)
    return JsonResponse({'data': render_to_string('UI_elements/rendered_notications.html', {'notifications': notifications}, request=request),
                         'last': number_pages == page + 1})


def get_notifications(request):
    request.session['notification_page'] += 1
    n, notifications, nn = get_page_data(Notification.objects.filter(status=NotificationsStatus.Actual.value).order_by('-date_of_creation'), request.session['notification_page'], 10)
    for notification in notifications:
        setattr(notification, 'name', NotificationsType.find_in_enum(notification.type).description)
        setattr(notification, 'type', NotificationsType.find_in_enum(notification.type).type)
        setattr(notification, 'date_delta', format_time(datetime.now(timezone.utc) - notification.date_of_creation))
    return n, notifications, nn

@staff_only
def user_list(request):
    users = Customer.get_all_customers()
    return page_render(request, 'admin_panel/main_page_admin_panel.html',
                       {'user_list': 'active', 'current_content_page': 'admin_panel/users/user_list.html', 'users': users})


@staff_only
def toggle_rss(request, user_pk):
    user = Customer.objects.get(pk=user_pk)
    user.include_in_email_delivery = not user.include_in_email_delivery
    user.save()
    return JsonResponse({'data': user.include_in_email_delivery, 'user_name': user.username})


@staff_only
def change_availability(request, user_pk):
    user = Customer.objects.get(pk=user_pk)
    user.is_active = not user.is_active
    user.save()
    return JsonResponse({'data': user.is_active, 'user_name': user.username})


@staff_only
def user_messages(request, user_pk=None):
    users = set(Customer.objects.exclude(pk=request.user.pk).filter(Q(sent_messages__isnull=False) | Q(pk=user_pk)))
    return page_render(request, 'admin_panel/main_page_admin_panel.html',
                       {'users_messages': 'active',
                        'current_content_page': 'admin_panel/messages/users_messages.html',
                        'users': users})


@staff_only
def chat_with_user(request, user_pk):
    return user_messages(request, user_pk)
