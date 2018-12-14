"""
Author: Christian R. Garcia
Data worker that waits for a queue to be filled with a job_id, once filled
the worker gets the job_dict, updates the job status, and executes the job.
Once done the status is again change, now from 'processing' to 'completed'.
Worker then begins waiting for a new job_id.
"""
import os
import uuid
import json
from datetime import datetime
import redis
from hotqueue import HotQueue

REDIS_IP = os.getenv("REDIS_IP")
REDIS_PORT = os.getenv("REDIS_PORT")
SPOTS_DB_ID = os.getenv("SPOTS_DB_ID")
JOB_DB_ID = os.getenv("JOB_DB_ID")
DATA_Q_DB_ID = os.getenv("DATA_Q_DB_ID")
GRAPH_Q_DB_ID = os.getenv("GRAPH_Q_DB_ID")
STAT_Q_DB_ID = os.getenv("STAT_Q_DB_ID")

SPOTS_DB = redis.StrictRedis(host=REDIS_IP, port=REDIS_PORT, db=SPOTS_DB_ID)
JOB_DB = redis.StrictRedis(host=REDIS_IP, port=REDIS_PORT, db=JOB_DB_ID)
DATA_Q = HotQueue("data_queue", host=REDIS_IP, port=REDIS_PORT, db=DATA_Q_DB_ID)
GRAPH_Q = HotQueue("graph_queue", host=REDIS_IP, port=REDIS_PORT, db=GRAPH_Q_DB_ID)
STATS_Q = HotQueue("stats_queue", host=REDIS_IP, port=REDIS_PORT, db=STAT_Q_DB_ID)


def _generate_jid():
    """
    Creates a jid for use in job identification.
    Returns jid.
    """
    return str(uuid.uuid4())


def _generate_job_key(jid):
    """
    Prepends 'job.' to jid for use as job key.
    Returns job_key.
    """
    return 'job.{}'.format(jid)


def _save_job(job_key, job_dict):
    """
    Takes job_key along with job_dictionary and creates/updates it in the JOB_DB.
    Allows for viewing the job and accessing it's information later.
    """
    JOB_DB.set(job_key, json.dumps(job_dict))


def _queue_job(job_key, work_type):
    """
    Takes job_key and a work type, 'data', 'graph', or 'stats' and adds
    the job_key to the corresponding queue to be used by workers.
    """
    if work_type == "data":
        DATA_Q.put(job_key)
    elif work_type == "graph":
        GRAPH_Q.put(job_key)
    elif work_type == "stats":
        STATS_Q.put(job_key)


def _create_job(jid, work_type, status, start, end, limit, offset, start_time, updated_time):
    """
    Takes parameters and creates a job_dict with them for use in queues and DB's.
    Returns job_dict.
    """
    if isinstance(jid, str):
        return {'id': jid,
                'status': status,
                'work type': work_type,
                'start': start,
                'end': end,
                'limit': limit,
                'offset': offset,
                'start time': start_time,
                'updated time': updated_time,
                'results': ""}

    return {'id': jid.decode('utf-8'),
            'status': status.decode('utf-8'),
            'work type': work_type.decode('utf-8'),
            'start': start.decode('utf-8'),
            'end': end.decode('utf-8'),
            'limit': limit.decode('utf-8'),
            'offset': offset.decode('utf-8'),
            'start time': start_time.decode('utf-8'),
            'updated time': updated_time.decode('utf-8'),
            'results': ""}


def add_job(work_type, start, end, limit, offset):
    """
    Creates job corresponding to it's inputted information and type.
    Returns to completed job_dict with information about the job.
    """
    jid = _generate_jid()
    job_key = _generate_job_key(jid)
    start_time = str(datetime.now())
    job_dict = _create_job(jid, work_type, "Submitted", start, end, limit,
                           offset, start_time, start_time)
    _save_job(job_key, job_dict)
    _queue_job(job_key, work_type)
    return json.dumps(job_dict)


def update_job(jid, new_status, results=""):
    """
    Takes jid, status and results.
    Updates job_db with new status and uploads results if they exist.
    """
    job_dict = json.loads(JOB_DB.get(_generate_job_key(str(jid))))
    updated_time = str(datetime.now())
    job_dict["updated time"] = updated_time
    job_dict["status"] = new_status
    if not job_dict["results"]:
        job_dict["results"] = results
    _save_job(_generate_job_key(str(jid)), job_dict)


def get_job(jid):
    """
    Takes a jid.
    Returns corresponding job_dict from JOB_DB.
    """
    if "job." in jid:
        jid = jid.replace("job.", "")
    job_dict = json.loads(JOB_DB.get(_generate_job_key(str(jid))))
    return job_dict


def get_all_jobs():
    """
    Returns a list of all job_dicts from the JOB_DB.
    """
    jobs_list = []
    for k in JOB_DB.keys():
        jobs_list.append(json.loads(JOB_DB.get(k)))
    return jobs_list
