import time
from celery.decorators import task
from celery.utils.log import get_task_logger
from django.db.models import F

from emails.models import EmailTemplate
from salarium.utils import send_email
from salarium.vk_integration import sync_vk_album_photos
from settings.models import Settings

logger = get_task_logger(__name__)


@task(name='send_email_template_task')
def send_email_template_task(template_pk, to, from_email=None, context=None):
    """Sends an email"""
    logger.info("Sent email template")
    template = EmailTemplate.objects.filter(pk=template_pk).first()
    send_email(template.body, template.subject, to, from_email=from_email, context=context)


@task(name='send_email_task')
def send_email_task(template, subject, to, from_email=None, context=None):
    """Sends an email"""
    logger.info("Sent email")

    send_email(template, subject, to, from_email=from_email, context=context)


@task(name='import_vk_album_photos')
def import_vk_album_photos(album_id):
    """Sends an email"""
    # print(Settings.objects.first().count_of_jobs)
    Settings.objects.update(count_of_jobs=F('count_of_jobs') - 1)

    time.sleep(1/3)

    sync_vk_album_photos(album_id)
