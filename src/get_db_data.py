"""
Author: Christian R. Garcia
Gets data from redis data database and parses it using start, end,
limit, and offset parameters. Results list of said data.
"""
import os
import json
import redis

REDIS_IP = os.getenv("REDIS_IP")
REDIS_PORT = os.getenv("REDIS_PORT")
SPOTS_DB_ID = os.getenv("SPOTS_DB_ID")

SPOTS_DB = redis.StrictRedis(host=REDIS_IP, port=REDIS_PORT, db=SPOTS_DB_ID)


def get_db_data(start, end, limit, offset):
    """
    Takes start, end, limit, and offset.
    Gets data from SPOTS_DB.
    Returns list with correct start, end, or limit, offset.
    """
    redis_data = json.loads(SPOTS_DB.get("data"))
    data_list = []
    limit_counter = 0

    for index, dict_x in enumerate(redis_data):
        year = dict_x['year']
        spots = dict_x['spots']

        if start is not None or end is not None:
            if start is None:
                if year <= end:
                    data_list.append({'id': index, 'year': year, 'spots': spots})
            elif end is None:
                if year >= start:
                    data_list.append({'id': index, 'year': year, 'spots': spots})
            elif year >= start and year <= end:
                data_list.append({'id': index, 'year': year, 'spots': spots})

        elif limit is not None or offset is not None:
            if limit is None:
                if index >= offset:
                    data_list.append({'id': index, 'year': year, 'spots': spots})
            elif offset is None:
                if limit_counter < limit:
                    data_list.append({'id': index, 'year': year, 'spots': spots})
                    limit_counter += 1
            elif index >= offset and limit_counter < limit:
                data_list.append({'id': index, 'year': year, 'spots': spots})
                limit_counter += 1

        else:
            data_list.append({'id': index, 'year': year, 'spots': spots})
    return data_list
