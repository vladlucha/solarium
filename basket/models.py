from __future__ import unicode_literals

import random
import string
import uuid
from uuid import uuid4

from django.core.validators import RegexValidator, MaxValueValidator, MinValueValidator
from django.db import models
from customer.models import Customer
from item.models import ItemSizeCountMap, Item
from salarium.enums import TransactionStatus, PaymentType, DeliveryType, DiscountType

default_transaction_code = '00001'
transaction_prefix_length = 4


def get_prefix():
    return ''.join(random.sample(string.ascii_lowercase, transaction_prefix_length)).upper()


class PromoCode(models.Model):
    code = models.CharField(max_length=150, unique=False, default=None)
    value = models.IntegerField(unique=False, default=0, validators=[
        MaxValueValidator(100),
        MinValueValidator(0)
    ])


class OrderHistory(models.Model):
    uuid = models.CharField(max_length=150, unique=False, default=uuid4().__str__())
    description = models.CharField(max_length=150, unique=False, default=None)
    date = models.DateTimeField(auto_now_add=True)


class Order(models.Model):
    uuid = models.CharField(max_length=150, unique=False, default=uuid4().__str__())
    purchaser = models.ForeignKey(Customer, default=None, null=True)
    item = models.ForeignKey(Item, default=None)
    count = models.IntegerField(default=0)
    items_sizes_count = models.ForeignKey(ItemSizeCountMap, default=None, related_name='orders')
    created_date = models.DateTimeField(auto_now_add=True)

    @property
    def total_price(self):
        return self.item.item_price * self.count

    @classmethod
    def create_order(cls, **kwargs):
        kwargs['uuid'] = str(uuid.uuid4())
        new_order = cls.objects.create(**kwargs)
        new_order.save()
        return new_order

    def update_order(self, **kwargs):
        self.__dict__.update(**kwargs)
        self.save()
        return self


class TransactionDetails(models.Model):
    uuid = models.CharField(max_length=150, unique=False, default=uuid4().__str__())
    purchaser_name = models.CharField(max_length=254, unique=False, default=None)
    purchaser_surname = models.CharField(max_length=254, unique=False, default=None)
    purchaser_patronymic = models.CharField(max_length=254, unique=False, default=None)
    purchaser_email = models.EmailField(blank=True, unique=False)
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number invalid.")
    purchaser_phone_number = models.CharField(validators=[phone_regex], blank=True, max_length=15, default=None)
    address = models.CharField(max_length=254, unique=False, default=None)
    city = models.CharField(max_length=254, unique=False, default=None)
    house = models.CharField(max_length=254, unique=False, default=None)
    housing_number = models.CharField(max_length=254, unique=False, default=None)
    flat_number = models.CharField(max_length=254, unique=False, default=None)
    post_index = models.CharField(max_length=254, unique=False, default=None)
    comment = models.CharField(max_length=554, unique=False, default=None)
    delivery_type = models.CharField(max_length=150, unique=False, default=DeliveryType.Post.value, choices=DeliveryType.choices())
    payment_type = models.CharField(max_length=150, unique=False, default=PaymentType.Cash.value, choices=PaymentType.choices())
    created_date = models.DateTimeField(auto_now_add=True)
    track_code = models.CharField(max_length=128, unique=False, null=True, default=None)
    promo_code = models.ForeignKey(PromoCode, null=True, default=None, related_name='transaction_details')
    credit_card_token = models.CharField(max_length=554, unique=False, default=None, null=True)

    @property
    def details_delivery_type(self):
        return DeliveryType.find_in_enum(self.delivery_type)

    @property
    def details_payment_type(self):
        return PaymentType.find_in_enum(self.payment_type)


class Transaction(models.Model):
    uuid = models.CharField(max_length=150, unique=False, default=uuid4().__str__())
    transaction_code = models.CharField(max_length=150, unique=False, default='{0}{1}'.format(get_prefix(), default_transaction_code))
    status = models.CharField(max_length=150, unique=False, default=TransactionStatus.Created.value,
                              choices=TransactionStatus.choices())
    orders = models.ManyToManyField(Order, default=None, related_name='transaction')
    transaction_details = models.ForeignKey(TransactionDetails, default=None, related_name='transaction')
    purchaser = models.ForeignKey(Customer, default=None, null=True)
    created_date = models.DateTimeField(auto_now_add=True)

    @property
    def applied_promocode(self):
        return next((disc for disc in self.transaction_discounts.all() if disc.discount_type == DiscountType.PromoCode.value), None)

    @property
    def transaction_status(self):
        return TransactionStatus.find_in_enum(self.status)

    @property
    def total_discount_value(self):
        return sum([d.discount_value for d in self.transaction_discounts.all()])

    @property
    def orders_sum_price(self):
        return sum([o.item.item_price * o.count for o in self.orders.all()])

    @property
    def total_price(self):
        price = self.orders_sum_price
        if self.transaction_details.payment_type == PaymentType.COD.value:
            price += self.delivery_additional_price
        return price - self.total_discount_value

    @property
    def delivery_additional_price(self):
        additional = 0
        if self.transaction_details.payment_type == PaymentType.COD.value:
            additional = (self.orders_sum_price * 0.02) + 3.5
        return additional

    @classmethod
    def create_transaction(cls, orders, **kwargs):
        purchaser = kwargs.pop('purchaser', None)
        transaction_details = TransactionDetails.objects.create(**kwargs)
        data = {'transaction_details': transaction_details,
                'purchaser': purchaser, 'uuid': uuid.uuid4(),
                'transaction_code': generate_transaction_code()}
        if kwargs['payment_type'] == PaymentType.CreditCard.value:
            data['status'] = TransactionStatus.Pending.value
        new_transaction = cls.objects.create(**data)
        new_transaction.orders = orders
        new_transaction.save()

        for order in orders:
            if order.item.active_sale:
                tr_discount = TransactionDiscounts.objects.create(**{
                    'discount_name': order.item.active_sale.name,
                    'discount_type': DiscountType.Sale.value,
                    'discount_value': order.item.price * (order.item.active_sale.rate / 100) * order.count,
                    'discount_rate': order.item.active_sale.rate
                })
                tr_discount.transaction = new_transaction
                tr_discount.order = order
                tr_discount.save()

        return new_transaction


def generate_transaction_code():
    last_transactions = Transaction.objects.order_by('-pk').last()
    prefix = get_prefix()
    code = default_transaction_code
    if last_transactions:
        code = last_transactions.transaction_code[5:]
    return '{0}{1}'.format(prefix, str(int(code) + 1).zfill(len(default_transaction_code)))


class TransactionDiscounts(models.Model):
    discount_name = models.CharField(max_length=150, unique=False, default='Sale')
    discount_type = models.CharField(max_length=150, unique=False, default=DiscountType.Sale.value, choices=DiscountType.choices())
    discount_value = models.IntegerField(default=0)
    discount_rate = models.IntegerField(unique=False, default=0, validators=[
        MaxValueValidator(100),
        MinValueValidator(0)
    ])
    created_date = models.DateTimeField(auto_now_add=True)
    transaction = models.ForeignKey(Transaction, default=None, null=True, related_name='transaction_discounts')
    order = models.ForeignKey(Order, default=None, null=True, related_name='order_discount')

