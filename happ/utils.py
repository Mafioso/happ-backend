import os
import uuid
import shutil
import colorsys
import dateutil
import datetime
import warnings
from calendar import timegm
from PIL import Image

from django.conf import settings
from django.template import loader
from django.core.mail import EmailMultiAlternatives

from rest_framework_jwt.settings import api_settings


def jwt_payload_handler(user):

    warnings.warn(
        'The following fields will be removed in the future: '
        '`email` and `user_id`. ',
        DeprecationWarning
    )

    from .serializers import UserPayloadSerializer
    payload = UserPayloadSerializer(user).data

    payload['exp'] = datetime.datetime.utcnow() + api_settings.JWT_EXPIRATION_DELTA
    if isinstance(user.pk, uuid.UUID):
        payload['user_id'] = str(user.pk)

    # Include original issued at time for a brand new token,
    # to allow token refresh
    if api_settings.JWT_ALLOW_REFRESH:
        payload['orig_iat'] = timegm(
            datetime.datetime.utcnow().utctimetuple()
        )

    if api_settings.JWT_AUDIENCE is not None:
        payload['aud'] = api_settings.JWT_AUDIENCE

    if api_settings.JWT_ISSUER is not None:
        payload['iss'] = api_settings.JWT_ISSUER

    return payload

def store_file(temp_path, dest_root, entity_id):
    if not temp_path:
        return ''
    if temp_path.find(dest_root) >= 0:
        return temp_path
    _, remaining_path = temp_path.split(settings.NGINX_TMP_UPLOAD_ROOT + '/')
    if not os.path.exists(os.path.join(dest_root, entity_id)):
        os.makedirs(os.path.join(dest_root, entity_id))
    file_path = os.path.join(dest_root, entity_id, remaining_path)
    try:
        shutil.move(temp_path, file_path)
    except:
        return ''
    return file_path

def date_to_string(d, format):
    if d is None:
        return d
    if isinstance(d, datetime.date) or isinstance(d, datetime.datetime):
        return datetime.datetime.strftime(datetime.datetime(d.year, d.month, d.day), format)
    if callable(d):
        return d()

    if not isinstance(d, basestring):
        return None

    # Attempt to parse a datetime:
    try:
        return datetime.datetime.strftime(dateutil.parser.parse(d), format)
    except (TypeError, ValueError):
        return None

def string_to_date(s, format):
    return datetime.datetime.strptime(date_to_string(s, format), format).date()

def time_to_string(t, format):
    if t is None:
        return t
    if isinstance(t, datetime.time) or isinstance(t, datetime.datetime):
        return datetime.datetime.strftime(datetime.datetime(1900, 1, 1, t.hour, t.minute, t.second), format)
    if callable(t):
        return t()

    if not isinstance(t, basestring):
        return None

    # Attempt to parse a datetime:
    try:
        datetime.datetime.strptime(t, format)
        return t
    except (TypeError, ValueError):
        return None

def string_to_time(s, format):
    if isinstance(s, datetime.time):
        return s
    if isinstance(s, datetime.datetime):
        return s.time()
    return datetime.datetime.strptime(s, format).time()

def average_color(path):

    try:
        image = Image.open(path)
    except IOError:
        return None

    w, h = image.size
    pixels = image.getcolors(w * h)

    most_frequent_pixel = pixels[0]

    for count, colour in pixels:
        if count > most_frequent_pixel[0]:
            most_frequent_pixel = (count, colour)

    rgb = most_frequent_pixel[1][:3]
    rgb = make_contrast(rgb)
    # hex value
    return '#{:02x}{:02x}{:02x}'.format(*rgb)

def make_contrast(rgb):
    while not is_contrast(rgb):
        rgb = rgb_0_1(*rgb)
        hls = colorsys.rgb_to_hls(*rgb)
        hls = decrease_lightness(*hls)
        rgb = colorsys.hls_to_rgb(*hls)
        rgb = rgb_0_255(*rgb)
    return rgb

def is_contrast(value):
    white = (255, 255, 255)
    white_g = [x/3294.0 if x <= 10 else (x/269.0 + 0.0513)**2.4 for x in white]
    value_g = [x/3294.0 if x <= 10 else (x/269.0 + 0.0513)**2.4 for x in value]
    white_l = 0.2126 * white_g[0] + 0.7152 * white_g[1] + 0.0722 * white_g[2]
    value_l = 0.2126 * value_g[0] + 0.7152 * value_g[1] + 0.0722 * value_g[2]
    if white_l > value_l:
        ratio = ((white_l + 0.05) / (value_l + 0.05))
    else:
        ratio = ((value_l + 0.05) / (white_l + 0.05))
    return ratio >= 7

def decrease_lightness(h, l, s):
    l -= 0.001
    return h, l, s

def rgb_0_1(*rgb):
    return [x/255.0 for x in rgb]

def rgb_0_255(*rgb):
    return [int(x*255) for x in rgb]

def send_mail(subject_template_name, email_template_name,
              context, from_email, to_email, html_email_template_name=None):
    """
    Sends a django.core.mail.EmailMultiAlternatives to `to_email`.
    """
    subject = loader.render_to_string(subject_template_name, context)
    # Email subject *must not* contain newlines
    subject = ''.join(subject.splitlines())
    body = loader.render_to_string(email_template_name, context)

    email_message = EmailMultiAlternatives(subject, body, from_email, [to_email])
    if html_email_template_name is not None:
        html_email = loader.render_to_string(html_email_template_name, context)
        email_message.attach_alternative(html_email, 'text/html')

    email_message.send()
