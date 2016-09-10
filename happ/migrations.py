from .models import get_db, pymongo


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
    pass


def migration__event__compound_index_by_status_and_city_for_feed__0004():
    event_coll = get_db()['event']
    event_coll.create_index([
        ('status', pymongo.ASCENDING),
        ('city', pymongo.ASCENDING)], background=True)


def migration__event__compound_index_by_status_and_geopoint_for_feed__0005():
    event_coll = get_db()['event']
    event_coll.create_index([
        ('geopoint', pymongo.GEO2D),
        ('status', pymongo.ASCENDING)], background=True)


def migration__event__compound_index_by_interests_and_end_date_and_end_time__0006():
    event_coll = get_db()['event']
    event_coll.create_index([
        ('interests', pymongo.ASCENDING),
        ('end_date', pymongo.ASCENDING),
        ('end_time', pymongo.ASCENDING)], background=True)

def migration__event__compound_index_by_interests_and_end_date_and_votes__0007():
    event_coll = get_db()['event']
    event_coll.create_index([
        ('interests', pymongo.ASCENDING),
        ('end_date', pymongo.ASCENDING),
        ('end_time', pymongo.DESCENDING)], background=True)
