"""
Author: Christian R. Garcia
File operations to allow initialization of data database, updating
of data database, and updating of data file. All done atomically
or using pipes to insure data is not used when being written.
"""
import os
import tempfile as tmp
from contextlib import contextmanager
import json
import operator
import redis

CSV_LOC = "sunspots.csv"

REDIS_IP = os.getenv("REDIS_IP")
REDIS_PORT = os.getenv("REDIS_PORT")
SPOTS_DB_ID = os.getenv("SPOTS_DB_ID")

SPOTS_DB = redis.StrictRedis(host=REDIS_IP, port=REDIS_PORT, db=SPOTS_DB_ID)

def init_db_data():
    """
    Once called, function will take CSV_FILE, parse it, and
    upload it to the SPOTS_DB for use throughout.
    """
    data_list = []
    with open(CSV_LOC, mode='r') as csv_file:
        for index, line in enumerate(csv_file):
            year, spots = line.split(',')
            year = int(year)
            spots = int(spots)
            data_list.append({'id': index, 'year': year, 'spots': spots})
    pipe_write_redis(data_list)
    print("Initial data upload to redis complete")


def pipe_write_redis(data):
    """
    Writes data to SPOTS_DB with pipeline to insure that no data
    is overwritten or corrupted due to race conditions.
    """
    pipe = SPOTS_DB.pipeline()
    pipe.set("data", json.dumps(data))
    pipe.execute()


def update_redis_and_csv(new_data):
    """
    Takes new_data, a json list and adds it to the current data in database.
    Sorts this new total set, correctly set 'ids' according to sorting and
    uploads data to redis with pipeline and writes to .csv atomically to
    insure uncorrupted read/writes.
    """
    data_list = json.loads(SPOTS_DB.get("data"))
    data_list += new_data
    data_list = sorted(data_list, key=operator.itemgetter('year'))
    for index, dict_x in enumerate(data_list):
        dict_x["id"] = int(index)

    pipe_write_redis(data_list)
    print("Redis updated")

    with open_atomic(CSV_LOC, 'w') as csv_file:
        for dict_x in data_list:
            row = ("{},{}\n").format(dict_x['year'], dict_x['spots'])
            csv_file.write(row)
    print("CSV updated")


@contextmanager
def tempfile(suffix='', dir=None):
    """
    From https://stackoverflow.com/questions/2333872/atomic-writing-to-file-with-python
    Creates tempfile to hold data before it is merged with sunspots.csv.
    """
    tmp_file = tmp.NamedTemporaryFile(delete=False, suffix=suffix, dir=dir)
    tmp_file.file.close()
    try:
        yield tmp_file.name
    finally:
        try:
            os.remove(tmp_file.name)
        except OSError as errors:
            if errors.errno == 2:
                pass
            else:
                raise


@contextmanager
def open_atomic(filepath, *args, **kwargs):
    """
    From https://stackoverflow.com/questions/2333872/atomic-writing-to-file-with-python
    Takes tempfile and atomically merges it with sunspots.csv to insure
    good read/writes.
    """
    fsync = kwargs.get('fsync', False)

    with tempfile(dir=os.path.dirname(os.path.abspath(filepath))) as tmppath:
        with open(tmppath, *args, **kwargs) as file:
            try:
                yield file
            finally:
                if fsync:
                    file.flush()
                    os.fsync(file.fileno())
        os.rename(tmppath, filepath)
