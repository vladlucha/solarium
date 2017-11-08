# -*- coding: utf-8 -*-
import inspect
from collections import namedtuple


class EnumWrapper:

    def __init__(self):
        pass

    @classmethod
    def find_in_enum(cls, value):
        return getattr(cls, value)

    @classmethod
    def choices(cls):
        # get all members of the class
        members = inspect.getmembers(cls, lambda m: not (inspect.isroutine(m)))
        # filter down to just properties
        props = [m for m in members if not (m[0][:2] == '__')]
        # format into django choice tuple
        choices = tuple([(str(p[1].value), p[0]) for p in props])
        return choices

    @classmethod
    def items(cls):
        # get all members of the class
        members = inspect.getmembers(cls, lambda m: not (inspect.isroutine(m)))
        # filter down to just properties
        props = [m for m in members if not (m[0][:2] == '__')]
        # format into django choice tuple
        choices = namedtuple(cls.__name__, [p[0] for p in props])
        # choices = namedtuple(((str(p[1].value), p[0]) for p in props])
        return choices(**{p[0]: p[1] for p in props})


class EnumField:
    value = None

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


class NotificationClassification(EnumWrapper):
    New = EnumField(value='new')
    Updated = EnumField(value='updated')


class NotificationsType(EnumWrapper):
    CommentAdded = EnumField(value='CommentAdded', description='New comment', type=NotificationClassification.New.value)
    CommentUpdated = EnumField(value='CommentUpdated', description='Comment was updated',
                               type=NotificationClassification.Updated.value)
    TransactionCreated = EnumField(value='TransactionCreated', description='Transaction was created',
                                   type=NotificationClassification.New.value)
    TransactionSend = EnumField(value='TransactionOrdersSend', description='Ordered items was sent',
                                type=NotificationClassification.Updated.value)
    TransactionCanceled = EnumField(value='TransactionCanceled', description='Transaction was canceled',
                                    type=NotificationClassification.Updated.value)
    TransactionProcessed = EnumField(value='TransactionProcessed', description='Transaction was processed',
                                     type=NotificationClassification.Updated.value)
    TransactionCompleted = EnumField(value='TransactionCompleted', description='Transaction successfully completed',
                                     type=NotificationClassification.Updated.value)


class NotificationsStatus(EnumWrapper):
    Actual = EnumField(value='Actual')
    Viewed = EnumField(value='Viewed')


class NotificationsScope(EnumWrapper):
    System = EnumField(value='System')
    User = EnumField(value='User')
    Admin = EnumField(value='Admin')


class TransactionStatus(EnumWrapper):
    Created = EnumField(value='Created', translate="Создано")
    PayDecline = EnumField(value='PayDecline', translate="Оплата отклонена")
    PayFail = EnumField(value='PayFail', translate="Ошибка оплаты")
    PayConfirmed = EnumField(value='PayConfirmed', translate="Оплата подтверждена")
    Pending = EnumField(value='Pending', translate="Ожидание оплаты")
    Completed = EnumField(value='Completed', translate="Успешно завершено")
    Canceled = EnumField(value='Canceled', translate="Закрыто")
    Sent = EnumField(value='Sent', translate="Отправлено")


class CreditCardPayment(EnumWrapper):
    success = EnumField(value='success', transaction_status=TransactionStatus.PayConfirmed)
    decline = EnumField(value='decline', transaction_status=TransactionStatus.PayDecline)
    fail = EnumField(value='fail', transaction_status=TransactionStatus.PayFail)
    cancel = EnumField(value='cancel', transaction_status=TransactionStatus.Canceled)


class PaymentType(EnumWrapper):
    ERIP = EnumField(value='Erip', translate="Чериз ЕРИП")
    CreditCard = EnumField(value='CreditCard', translate="Банковской картой")
    COD = EnumField(value='COD', translate="Наложенным платежом")
    Cash = EnumField(value='Cash', translate="Наличными курьеру")


class DiscountType(EnumWrapper):
    Sale = EnumField(value='Sale', translate="Скидка")
    PromoCode = EnumField(value='PromoCode', translate="Промокод")


class DeliveryType(EnumWrapper):
    Post = EnumField(value='Post', translate="Доставка наложенным платежом", additional="(РУП 'Белпочта')",
                     payment_types=[PaymentType.COD, PaymentType.ERIP, PaymentType.CreditCard])
    CourierVitebsk = EnumField(value='CourierMinsk', translate="Доставка по адресу г.Витебск", additional="(Бесплатно)",
                               payment_types=[PaymentType.Cash, PaymentType.ERIP, PaymentType.CreditCard])
    CourierMinsk = EnumField(value='CourierMinsk', translate="Доставка курьером по г.Минск", additional="(Бесплатно)",
                             payment_types=[PaymentType.Cash, PaymentType.CreditCard])


class EntityStatus(EnumWrapper):
    Pending = EnumField(value="Pending", translate="Ожидание")
    Published = EnumField(value="Published", translate="Опубликовано")
    Trashed = EnumField(value="Trashed", translate="Удалено")