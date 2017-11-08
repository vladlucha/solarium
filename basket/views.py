import json

from django.http import HttpResponse
from django.http import JsonResponse

# Create your views here.
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from requests.auth import HTTPBasicAuth

from basket.models import Order, Transaction, TransactionDetails, PromoCode, TransactionDiscounts
from item.models import ItemSizeCountMap, Item
from notifications.models import Notification
from salarium.enums import NotificationsType, TransactionStatus, DeliveryType, PaymentType, DiscountType, \
    CreditCardPayment
from salarium.utils import page_render, format_form_data, parse_int, staff_only
from salarium.tasks import send_email_task


def get_orders_list(request):
    if 'transaction_pk' in request.session:
        transaction = Transaction.objects.filter(pk=request.session['transaction_pk']).first()
        return transaction.orders.all()

    return Order.objects.filter(purchaser=request.user,
                                transaction__isnull=True).all() if request.user.is_authenticated() else \
        Order.objects.filter(purchaser=None, uuid__in=request.session.get('orders', [])).all()


def calculate_promocode_if_exists(request, total_price):
    if 'promocode' in request.session and request.session['promocode']['value']:
        total_discount = total_price * request.session['promocode']['value']
        return total_discount, total_price - total_discount
    return 0, 0


def get_orders(request, step=None, transaction=None):
    context = {'delivery_types': DeliveryType.items(), 'payment_types': PaymentType.items(), 'step': step,
               'orders': get_orders_list(request) if not transaction else transaction.orders.all()}

    context['total_price'] = sum([o.item.item_price * o.count for o in context['orders']])

    if 'promocode' in request.session and request.session['promocode']['value']:
        context['total_discount'], context['discount_price'] = calculate_promocode_if_exists(request, context['total_price'])

    return page_render(request, 'site/basket/basket.html', context)


def render_step(request, transaction_pk, step):
    transaction = Transaction.objects.filter(pk=transaction_pk).first()
    return get_orders(request, step=step, transaction=transaction)


@csrf_exempt
def change_order_count(request, order_uuid):
    if request.method == 'POST':
        order = Order.objects.filter(uuid=order_uuid)
        if order.exists():
            order = order.first()
            max = order.items_sizes_count.current_count
            delta = parse_int(request.POST.get('delta'), 0)
            order.count += delta

            if order.count < 1:
                order.count = 1
            elif order.count > max:
                order.count = max

            order.save()

        total_price = sum([o.item.item_price * o.count for o in get_orders_list(request)])
        total_discount, discount_price = calculate_promocode_if_exists(request, total_price)
        return JsonResponse({'code': 200, 'total_discount': total_discount, 'discount_price': discount_price,
                             'count': order.count, 'total_price': total_price})
    return JsonResponse({'code': 401})


def create_order(request):
    if request.method == 'POST':
        data = json.loads(request.POST.get('data'))
        items_sizes_pk = None
        item = None
        for item_size_count in data:
            if item_size_count['name'] != 'item-pk' and item_size_count['value'] == 'on':
                items_sizes_pk = parse_int(item_size_count['name'])
            elif item_size_count['name'] == 'item-pk':
                item = Item.objects.get(pk=int(item_size_count['value']))

        item_size = ItemSizeCountMap.objects.filter(pk=items_sizes_pk).first()

        if item_size:
            order = Order.objects.filter(purchaser=request.user, item=item, items_sizes_count=item_size,
                                         transaction__isnull=True)
            if not order.exists():
                order = create_user_order(request, item, item_size)
            else:
                order = order.first()
                order.count += 1
                order.save()
            if not request.user.is_authenticated():
                if 'orders' in request.session and isinstance(request.session['orders'], list):
                    request.session['orders'] += [order.uuid]
                else:
                    request.session['orders'] = [order.uuid]

            orders = Order.objects.exclude(items_sizes_count__isnull=True).filter(items_sizes_count__pk=item_size.pk).all()
            return JsonResponse({'code': 200, 'size_count_pk': item_size.pk,
                                 'count': item_size.count - sum([o.count for o in orders])})
        return JsonResponse({'code': 401})


def create_user_order(request, item, item_size):
    return Order.create_order(**{'purchaser': request.user if request.user.is_authenticated() else None,
                                 'item': item,
                                 'count': 1,
                                 'items_sizes_count': item_size})


@csrf_exempt
def delete_order(request, order_uuid):
    if Order.objects.filter(uuid=order_uuid).exists():
        Order.objects.filter(uuid=order_uuid).delete()
        return JsonResponse({'code': 200})
    return JsonResponse({'code': 401})


@csrf_exempt
def create_transaction(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        if 'form_data' in data and 'orders_uuids' in data:
            form_data = format_form_data(TransactionDetails, data['form_data'])
            orders = Order.objects.filter(uuid__in=data['orders_uuids'])
            for order in orders:
                size_count = order.items_sizes_count
                size_count.count -= order.count

                if size_count.count < 1:
                    size_count.count = 0
                size_count.save()

            form_data['purchaser'] = request.user
            transaction = Transaction.create_transaction(orders, **form_data)

            if 'promocode' in request.session and request.session['promocode']['value']:
                tr_discount = TransactionDiscounts.objects.create(**{
                    'discount_name': request.session['promocode']['code'],
                    'discount_type': DiscountType.PromoCode.value,
                    'discount_value': transaction.total_price * request.session['promocode']['value'],
                    'discount_rate': request.session['promocode']['value'] * 100
                })
                tr_discount.transaction = transaction
                tr_discount.save()
                del request.session['promocode']

            send_email_task.delay('Тут это, вы чет купили!', 'ПАКУБКА', [transaction.purchaser.email], 'mail@salarium.by')

            Notification.create_notification(**{'type': NotificationsType.TransactionCreated.value,
                                                'entity_pk': transaction.pk})

            if transaction.transaction_details.payment_type == PaymentType.CreditCard.value:
                return get_credit_card_token(request, transaction)
            return JsonResponse({'code': 200})
    return JsonResponse({'code': 401})


@staff_only
def admin_orders(request, order_status):
    if not order_status:
        order_status = TransactionStatus.Created.value
    transactions = Transaction.objects.filter(status=order_status).all()
    count = {}
    for status in TransactionStatus.items():
        count[status.value] = Transaction.objects.filter(status=status.value).count()
    return page_render(request, 'admin_panel/main_page_admin_panel.html',
                       {'admin_orders': 'active',
                        'current_content_page': 'admin_panel/orders/orders_list.html',
                        'statuses': TransactionStatus.items(), 'selected_status': order_status,
                        'transactions': transactions, 'full_width': True, 'count': count})


@staff_only
def get_transaction(request, transaction_uuid):
    transaction = Transaction.objects.filter(uuid=transaction_uuid).first()
    if transaction:
        return page_render(request, 'admin_panel/main_page_admin_panel.html',
                           {'admin_orders': 'active',
                            'current_content_page': 'admin_panel/orders/transaction_details.html',
                            'transaction': transaction, 'statuses': TransactionStatus.items()})
    return redirect(request.META.get('HTTP_REFERER'))


@staff_only
def modify_transaction(request, transaction_uuid):
    if request.method == 'POST':
        transaction = Transaction.objects.filter(uuid=transaction_uuid).first()
        transaction.status = request.POST.get('status', '')
        transaction.transaction_details.track_code = request.POST.get('track_code', '')
        transaction.transaction_details.save()
        transaction.save()
    return redirect('get_transaction', transaction_uuid=transaction_uuid)


def check_promocode(request):
    if request.method == 'POST':
        promocode = request.POST.get('promocode', None)
        request.session['promocode'] = {'code': promocode, 'value': None}

        existing_promocode = PromoCode.objects.filter(code=promocode).first()
        if existing_promocode:
            request.session['promocode'].update({'value': existing_promocode.value / 100})

    return redirect('basket')


def get_credit_card_token(request, transaction):
    import requests
    response = requests.post(
        "https://checkout.bepaid.by/ctp/api/checkouts",
        auth=HTTPBasicAuth('1054', 'f3f3e1da3c746e93bcdad34a8ac73b370e4da064738a272d935e0ced1b40342a'),
        data=json.dumps({
            'checkout': {
                'version': 2,
                'transaction_type': 'payment',
                "order": {
                    "amount": int('{:10.0f}'.format(transaction.total_price * 100)),
                    "currency": "BYN",
                    "description": "Тестовый заказ"
                },
                "customer": {
                    "address": transaction.transaction_details.address,
                    "city": transaction.transaction_details.city,
                    "first_name": transaction.transaction_details.purchaser_name,
                    "last_name": transaction.transaction_details.purchaser_surname,
                    "phone": transaction.transaction_details.purchaser_phone_number,
                    "email": transaction.transaction_details.purchaser_email,
                },
                "settings": {
                    "success_url": "http://127.0.0.1:8000/basket/payment/success",
                    "decline_url": "http://127.0.0.1:8000/basket/payment/decline",
                    "fail_url": "http://127.0.0.1:8000/basket/payment/fail",
                    "cancel_url": "http://127.0.0.1:8000/basket/payment/cancel",
                    "language": "ru",
                    "customer_fields": {
                        "hidden": ["phone"],
                        "read_only": ["email", "phone", "first_name", "last_name"]
                    },
                },
            }
        }),
        headers={'accept': 'application/json', 'content-type': 'application/json'}
    )

    transaction.transaction_details.credit_card_token = json.loads(response.text)['checkout']['token']
    transaction.transaction_details.save()
    request.session['transaction_pk'] = transaction.pk

    return HttpResponse(response)


def change_payment_status(request, payment_status):
    transaction = Transaction.objects.filter(transaction_details__credit_card_token=request.GET.get('token')).first()
    payment_status = CreditCardPayment.find_in_enum(payment_status)
    if payment_status:
        transaction.status = payment_status.transaction_status.value
        transaction.save()

    request.session.pop('transaction_pk')

    return redirect('render_step', step='slide4', transaction_pk=transaction.pk)

