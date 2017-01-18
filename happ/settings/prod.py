from .common import *

MONGODB_NAME = 'happ_prod'

DEBUG = False
STATIC_ROOT = os.path.join('/', 'static')

GOOGLE_BROWSER_KEY = 'AIzaSyDi4DJypjXFrG68LVJU6EGdK-rHryYVyRw'
GOOGLE_API_KEY = 'AIzaSyCD8N02qqKXT5QHEWt8jk28F2AJ8kKIsrA'
ANYMAIL = {
    "MAILGUN_API_KEY": "key-4954691d2cfc091f07b80b0100806dc7",
    "MAILGUN_SENDER_DOMAIN": 'notifications.happapp.info',
}
DEFAULT_FROM_EMAIL = 'no-reply@notifications.happapp.info'
