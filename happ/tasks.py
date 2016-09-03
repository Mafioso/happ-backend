from __future__ import absolute_import

from celery import shared_task
from celery.utils.log import get_task_logger
from django.conf import settings

from .integrations import translate
from .models import Event, Localized


logger = get_task_logger(__name__)

@shared_task
def translate_event(id, target):
    logger.info("Starting translation for event: %s" % id)
    event = Event.objects.get(id=id)
    data = {}
    for field in Event.localized_fields:
        tmp = translate.translate(string=getattr(event, field), target=target)
        data[field] = tmp['data']['translations'][0]['translatedText']
    try:
        l = Localized.objects.get(entity=event, language=target)
    except Localized.DoesNotExist:
        l = Localized(entity=event, language=target)
    l.data = data
    l.save()
    logger.info("Finished translation for event: %s" % id)
