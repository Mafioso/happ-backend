from __future__ import absolute_import

from django.conf import settings

from celery import shared_task
from celery.utils.log import get_task_logger

from .integrations import google
from .models import Localized


logger = get_task_logger(__name__)

@shared_task
def translate_entity(cls, id, target):
    logger.info("Starting translation for {}: {}".format(cls.__name__, id))
    entity = cls.objects.get(id=id)
    data = {}
    for field in cls.localized_fields:
        tmp = google.translate(string=getattr(entity, field), target=target)
        data[field] = tmp['data']['translations'][0]['translatedText']
    try:
        l = Localized.objects.get(entity=entity, language=target)
    except Localized.DoesNotExist:
        l = Localized(entity=entity, language=target)
    l.data = data
    l.save()
    logger.info("Finished translation for {}: {}".format(cls.__name__, id))
