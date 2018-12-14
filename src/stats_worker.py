"""
Author: Christian R. Garcia
Stats worker that waits for a queue to be filled with a job_id, once filled
the worker gets the job_dict, updates the job status, and executes the job.
Once done the status is again change, now from 'processing' to 'completed'.
Worker then begins waiting for a new job_id.
"""
import os
from time import sleep
import statistics
from hotqueue import HotQueue
import jobs
from get_db_data import get_db_data

REDIS_IP = os.getenv("REDIS_IP")
REDIS_PORT = os.getenv("REDIS_PORT")
STAT_Q_DB_ID = os.getenv("STAT_Q_DB_ID")

# Waits until redis is in operation and queue can be initialized.
while True:
    try:
        STATS_Q = HotQueue("stats_queue", host=REDIS_IP, port=REDIS_PORT, db=STAT_Q_DB_ID)
        STATS_Q.get()
        break
    except:
        print("Error: Redis not yet initialized. Reattempting connection in 3 seconds")
        sleep(3)


@STATS_Q.worker
def stats_worker(job_id):
    """
    Decorator waits for queue to have a job put in it. Once an item
    is put in queue the graph worker takes the job_id, gets the job_dict
    updates job status, executes the job, updates job's dictionary 'results'
    key to the results of the function, updates status again to complete
    and prints out "job_id + complete" to console.
    """
    job_dict = jobs.get_job(job_id)
    jobs.update_job(job_dict["id"], "Processing")
    results = execute_job(job_dict)
    jobs.update_job(job_dict["id"], "Completed", results)
    print(job_id + " complete")


def execute_job(job_dict):
    """
    Takes job_dict as input.
    Gets the data from get_db_data so data bounds are correct.
    Runs 'statistics' operations on the data_set and places in a 'result's dictionary.
    Returns dictionary as results
    """
    data_list = get_db_data(job_dict["start"], job_dict["end"],
                            job_dict["limit"], job_dict["offset"])

    sun_data = [dict_x["spots"] for dict_x in data_list]

    if sun_data:
        stats_list = [
            {"mean": statistics.mean(sun_data)},
            {"harmonic mean": statistics.harmonic_mean(sun_data)},
            {"median": statistics.median(sun_data)},
            {"low median": statistics.median_low(sun_data)},
            {"high median": statistics.median_high(sun_data)},
            {"mode": statistics.mode(sun_data)},
            {"variance": statistics.variance(sun_data)},
            {"standard deviation": statistics.stdev(sun_data)},]
    return stats_list


if __name__ == "__main__":
    print("Stats worker running")
    stats_worker()
