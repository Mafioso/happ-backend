import os
import uuid
import shutil
import warnings
from calendar import timegm
from datetime import datetime

from django.conf import settings

from rest_framework_jwt.settings import api_settings

from .serializers import UserPayloadSerializer


def jwt_payload_handler(user):

    warnings.warn(
        'The following fields will be removed in the future: '
        '`email` and `user_id`. ',
        DeprecationWarning
    )

    payload = UserPayloadSerializer(user).data

    payload['exp'] = datetime.utcnow() + api_settings.JWT_EXPIRATION_DELTA
    if isinstance(user.pk, uuid.UUID):
        payload['user_id'] = str(user.pk)

    # Include original issued at time for a brand new token,
    # to allow token refresh
    if api_settings.JWT_ALLOW_REFRESH:
        payload['orig_iat'] = timegm(
            datetime.utcnow().utctimetuple()
        )

    if api_settings.JWT_AUDIENCE is not None:
        payload['aud'] = api_settings.JWT_AUDIENCE

    if api_settings.JWT_ISSUER is not None:
        payload['iss'] = api_settings.JWT_ISSUER

    return payload

def store_file(temp_path):
    _, remaining_path = temp_path.split(settings.NGINX_TMP_UPLOAD_ROOT + '/')
    file_path = os.path.join(settings.NGINX_UPLOAD_ROOT, remaining_path)
    shutil.move(temp_path, file_path)
    return file_path
