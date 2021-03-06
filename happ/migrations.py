import os
import json
import datetime
import random
import pymongo

from django.conf import settings

from .models import get_db
from .utils import average_color, daterange, string_to_date, date_to_string, make_random_password
from .integrations.quickblox import signup as quickblox_signup

def migration__user__change_interests_schema__0001():
    user_coll = get_db()['user']
    interest_coll = get_db()['interest']
    # 1. for each user do |user|
    # 2. for each user interest find possible cities and make the following substructure {city: cityX, ints: []}
    # 3. build new array structure for each user interests field where each item is substructure defined by interest in previous point:
        # interests: [{city: cityX, ints: []},{city: cityX, ints: []}]
    _interest_ids = []
    [_interest_ids.extend(user_data['interests']) for user_data in user_coll.find({})]
    interest_map = {str(_int['_id']):_int for _int in interest_coll.find({"_id": {"$in": _interest_ids}})}

    for user_data in user_coll.find({}):
        user_interests = []
        for interest_id in map(str, user_data['interests']):
            interest_obj = interest_map[interest_id]
            for city_id in map(str, interest_obj['local_cities']):
                _idx = -1
                for i, city_interests in enumerate(user_interests):
                    if city_interests['c'] == city_id:
                        _idx = i
                        break
                if _idx == -1:
                    user_interests.append({'c': city_id, 'ins': [interest_id]})
                else:
                    user_interests[_idx]['ins'].append(interest_id)
        user_coll.update({'_id': user_data['_id']}, {'$set': {'interests': user_interests}})

def migration__user__add_multikey_index_on_interests__0002():
    # CAREFUL: probably we do not need it because we always do search queries by user_id and there is always index by _id. Fetch by user_id locates a single document so index is utilized fully.
    user_coll = get_db()['user']
    user_coll.create_index([("interests.c", pymongo.ASCENDING), ("interests.ins", pymongo.ASCENDING)], background=True)

def migration__event__upvotes_is_embed__0003():
    event_coll = get_db()['event']
    user_coll = get_db()['user']
    ucount = user_coll.count()
    users = list(user_coll.find())
    _now = datetime.datetime.utcnow()
    for ev in event_coll.find({}):
        if isinstance(ev['votes'], list):
            continue
        uidx = random.randint(1, ucount) - 1
        upvotes = [{'user': users[uidx]['_id'], 'ts': _now} for _ in xrange(ev['votes'] % 4)]
        event_coll.update({'_id': ev['_id']}, {'$set': {'votes': upvotes, 'votes_num': len(upvotes)}})

def migration__event__compound_index_by_world__0004():
    event_coll = get_db()['event']
    event_coll.create_index([
        ('interests', pymongo.ASCENDING),
        ('end_date', pymongo.ASCENDING),
        ('end_time', pymongo.ASCENDING)], background=True)
    event_coll.create_index([
        ('interests', pymongo.ASCENDING),
        ('end_date', pymongo.ASCENDING),
        ('votes_num', pymongo.DESCENDING)], background=True)

def migration__event__compound_index_by_interests_and_end_date_and_votes_or_time__0005():
    event_coll = get_db()['event']
    event_coll.create_index([
        ('geopoint', pymongo.GEO2D),
        ('status', pymongo.ASCENDING),
        ('interests', pymongo.ASCENDING),
        ('end_date', pymongo.ASCENDING),
        ('end_time', pymongo.DESCENDING)], background=True)
    event_coll.create_index([
        ('geopoint', pymongo.GEO2D),
        ('status', pymongo.ASCENDING),
        ('interests', pymongo.ASCENDING),
        ('end_date', pymongo.ASCENDING),
        ('votes_num', pymongo.DESCENDING)], background=True)

    event_coll.create_index([
        ('status', pymongo.ASCENDING),
        ('city', pymongo.ASCENDING),
        ('interests', pymongo.ASCENDING),
        ('end_date', pymongo.ASCENDING),
        ('end_time', pymongo.DESCENDING)], background=True)
    event_coll.create_index([
        ('status', pymongo.ASCENDING),
        ('city', pymongo.ASCENDING),
        ('interests', pymongo.ASCENDING),
        ('end_date', pymongo.ASCENDING),
        ('votes_num', pymongo.DESCENDING)], background=True)

def migration__user__remove_field_favourites__0006():
    user_coll = get_db()['user']
    user_coll.update({}, {'$unset': {'favorites': ''}}, multi=True)

def migration__event__add_index_by_infavourites__0007():
    event_coll = get_db()['event']
    event_coll.create_index([
        ('in_favourites', pymongo.ASCENDING),
        ('end_date', pymongo.ASCENDING),
        ('end_time', pymongo.DESCENDING)], background=True)
    event_coll.create_index([
        ('in_favourites', pymongo.ASCENDING),
        ('end_date', pymongo.ASCENDING),
        ('votes_num', pymongo.DESCENDING)], background=True)

def migration__user__set_default_role__0008():
    user_coll = get_db()['user']
    for user_data in user_coll.find({}):
        if 'role' not in user_data:
            user_coll.update({'_id': user_data['_id']}, {'$set': {'role': 0}})

def migration__city__set_is_active__0009():
    coll = get_db()['city']
    coll.update({}, {'$set': {'is_active': True}}, multi=True)

def migration__interest__set_is_active__0010():
    coll = get_db()['interest']
    coll.update({}, {'$set': {'is_active': True}}, multi=True)

def migration__event__remove_field_images__0011():
    coll = get_db()['event']
    coll.update({}, {'$unset': {'images': ''}}, multi=True)

def migration__event__fill_max_age_field__0012():
    coll = get_db()['event']
    for data in coll.find({}):
        if 'age_restriction' in data:
            coll.update({'_id': data['_id']}, {'$set': {'max_age': data['age_restriction']}})

def migration__event__remove_field_age_restriction__0013():
    coll = get_db()['event']
    coll.update({}, {'$unset': {'age_restriction': ''}}, multi=True)

def migration__event__fill_place_name_field__0014():
    coll = get_db()['event']
    coll.update({}, {'$set': {'place_name': ''}}, multi=True)

def migration__file_object__fill_color_field__0015():
    coll = get_db()['file_object']
    for data in coll.find({}):
        coll.update({'_id': data['_id']}, {'$set': {'color': average_color(data['path'])}})

def migration__event__remove_field_color__0016():
    coll = get_db()['event']
    coll.update({}, {'$unset': {'color': ''}}, multi=True)

def migration__interest__remove_field_color__0017():
    coll = get_db()['interest']
    coll.update({}, {'$unset': {'color': ''}}, multi=True)

def migration__countries_and_currencies__0018():
    coll = get_db()['country']
    curr_coll = get_db()['currency']
    with open(os.path.join(settings.BASE_DIR, 'happ/fixtures/countries.json'), 'r') as f:
        s = json.loads(f.read())
        for country in coll.find({}):
            for item in s:
                if country['name'] == item['country']:
                    for currency in curr_coll.find({}):
                        if currency['name'] == item['currency']:
                            coll.update({'_id': country['_id']}, {'$set': {'currency': currency['_id']}})
    for currency in curr_coll.find({}):
        for item in s:
            if currency['name'] == item['currency']:
                curr_coll.update({'_id': currency['_id']}, {'$set': {'code': item['code']}})
    for currency in curr_coll.find({}):
        if 'code' not in currency:
            curr_coll.remove({'_id': currency['_id']})

def migration__event__fill_place_name_field__0019():
    coll = get_db()['event']
    coll.update({}, {'$set': {'is_active': True}}, multi=True)

def migration__event_time__0020():
    coll = get_db()['event']
    # coll2 = get_db()['event_time']
    for event in coll.find({}):
        if 'start_date' not in event or 'end_date' not in event:
            continue
        start_date = event['start_date']
        end_date = event['end_date']
        data = [{
            'date': date_to_string(date, settings.DATE_STRING_FIELD_FORMAT),
            'start_time': event['start_time'] if 'start_time' in event else '000000',
            'end_time': event['end_time'] if 'end_time' in event else '235959',
            # 'event': event['_id'],
        } for date in daterange(string_to_date(start_date, settings.DATE_STRING_FIELD_FORMAT), string_to_date(end_date, settings.DATE_STRING_FIELD_FORMAT))]
        coll.update({'_id': event['_id']}, {'$set': {'datetimes': data}})
    coll.update({}, {'$unset': {'start_date': ''}}, multi=True)
    coll.update({}, {'$unset': {'end_date': ''}}, multi=True)
    coll.update({}, {'$unset': {'start_time': ''}}, multi=True)
    coll.update({}, {'$unset': {'end_time': ''}}, multi=True)

def migration__city_geopoint__0021():
    coll = get_db()['city']
    for city in coll.find({}):
        if 'geopoint' in city and isinstance(city['geopoint'], list):
            coll.update(
                {'_id': city['_id']},
                {'$set': {'geopoint': { "type" : "Point", "coordinates" : city['geopoint'] }}}
            )

def migration__event_geopoint__0022():
    coll = get_db()['event']
    for event in coll.find({}):
        if 'geopoint' in event and isinstance(event['geopoint'], list):
            coll.update(
                {'_id': event['_id']},
                {'$set': {'geopoint': { "type" : "Point", "coordinates" : event['geopoint'] }}},
            )

def migration__event_to_feed__0023():
    coll = get_db()['event']
    feed = get_db()['feed']
    for event in coll.find({}):
        if 'datetimes' in event and isinstance(event['datetimes'], list):
            for date in event['datetimes']:
                feed.insert({'event': event['_id'], 'datetimes': [date]})

def migration__user_to_quickblox__0024():
    users = get_db()['user']
    for user in users.find({ "quickblox_login": { '$not': { '$exists': True } } }):
        quickblox_password = make_random_password()
        quickblox_user = quickblox_signup(user.get('username'), quickblox_password)
        if 'errors' not in quickblox_user:
            users.update(
                    {'_id': user.get('_id')},
                    {'$set': {'quickblox_id': str(quickblox_user['user']['id']), 'quickblox_password': quickblox_password, 'quickblox_login': str(quickblox_user['user']['login'])}}
                    )

def migration__user_to_quickblox_empty__0025():
    users = get_db()['user']
    for user in users.find({}):
        if 'quickblox_id' not in user and user.get('quickblox_id'):
            users.update(
                {'_id': user.get('_id')},
                {'$set': {'quickblox_id': int(user.get('quickblox_id',''))}}
                    )
