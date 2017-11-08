from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.http import JsonResponse
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from lazysignup.decorators import require_nonlazy_user
from basket.models import Transaction
from customer.models import Customer
from emails.models import EmailRecipients
from media_library.models import Media
from salarium.utils import page_render, get_page_data, get_page_number


@login_required(login_url='/')
@require_nonlazy_user()
def get_profile(request):
    return page_render(request, 'site/profile/profile.html', {})


@login_required(login_url='/')
def get_user_messages(request):
    sent_messages = request.user.sent_messages.order_by('-timestamp')
    received_messages = request.user.received_messages.order_by('-timestamp')
    messages = reversed(sent_messages | received_messages)
    return page_render(request, 'site/profile/messages.html', {'messages': messages})


@login_required(login_url='/')
def get_user_orders(request, page_number=1):
    page_number = get_page_number(page_number)

    transactions_page, transactions, number_transactions_pages = get_page_data(Transaction.objects.filter(purchaser__pk=request.user.id).order_by('pk').all(),
                                                                               page_number, 5)

    context = {'transactions_page': transactions_page, 'transactions': transactions, 'number_transactions_pages': range(1, number_transactions_pages)}
    return page_render(request, 'site/profile/orders.html', context)


@login_required(login_url='/')
@require_nonlazy_user()
def save_profile(request):
    context = {
        'alert_type': 'warning',
        'alert_message': 'Error occur'
    }
    username = request.POST.get('username', '')
    if request.method == 'POST':
        if Customer.objects.filter(username=username).exists() and request.user.username != username:
            context['alert_message'] = 'User with this username already exists'
        else:
            context['alert_type'] = 'notice'
            context['alert_message'] = 'Profile successfully updated'
            thumb_id = request.POST.get('thumbnail')
            request.user.update(**{
                'username': username,
                'thumbnail': Media.objects.filter(pk=thumb_id if thumb_id != '' else None).first(),
                'name': request.POST.get('purchaser_name', ''),
                'surname': request.POST.get('purchaser_surname', ''),
                'patronymic': request.POST.get('purchaser_patronymic', ''),
                'email': request.POST.get('purchaser_email', ''),
                'phone_number': request.POST.get('purchaser_phone_number', ''),
                'address': request.POST.get('address', ''),
                'house': request.POST.get('house', ''),
                'housing_number': request.POST.get('housing_number', ''),
                'flat_number': request.POST.get('flat_number', ''),
                'post_index': request.POST.get('post_index', ''),
                'include_in_email_delivery': request.POST.get('delivery', '') == 'on',
            })
            request.user.save()

    return redirect('profile')


@login_required(login_url='/')
def toggle_view(request, view_type):
    if view_type in ['list', 'items']:
        request.session['view_type'] = view_type
    return redirect(request.META.get('HTTP_REFERER', '/'))


def add_to_rss(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        request.session['include_in_email_delivery'] = True
        if request.user.is_authenticated:
            request.user.include_in_email_delivery = True
            request.user.save()
        elif email and not EmailRecipients.objects.filter(email_address=email).exists():
            new_recipient = EmailRecipients.objects.create(email_address=email, is_active=True)
            new_recipient.save()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    return redirect('news')


@login_required(login_url='/')
@csrf_exempt
def change_thumbnail(request):
    if request.method == 'POST':
        image = Media.objects.filter(pk=request.POST.get('image_pk')).first()
        if image:
            request.user.thumbnail = image
            request.user.save()
            return JsonResponse({'code': 200})
    return JsonResponse({'code': 401})

