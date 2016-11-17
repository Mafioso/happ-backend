import datetime
import random
import pymongo
from .models import get_db, User


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
