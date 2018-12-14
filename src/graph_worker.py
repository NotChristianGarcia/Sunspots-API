"""
Author: Christian R. Garcia
Graph worker that waits for a queue to be filled with a job_id, once filled
the worker gets the job_dict, updates the job status, and executes the job.
Once done the status is again change, now from 'processing' to 'completed'.
Worker then begins waiting for a new job_id.
"""
import os
from time import sleep
import requests as r
import matplotlib.pyplot as plt
from hotqueue import HotQueue
import jobs
from get_db_data import get_db_data

REDIS_IP = os.getenv("REDIS_IP")
REDIS_PORT = os.getenv("REDIS_PORT")
GRAPH_Q_DB_ID = os.getenv("GRAPH_Q_DB_ID")

# Waits until redis is in operation and queue can be initialized.
while True:
    try:
        GRAPH_Q = HotQueue("graph_queue", host=REDIS_IP, port=REDIS_PORT, db=GRAPH_Q_DB_ID)
        GRAPH_Q.get()
        break
    except:
        print("Error: Redis not yet initialized. Reattempting connection in 3 seconds")
        sleep(3)


@GRAPH_Q.worker
def graph_worker(job_id):
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
    Takes the list and grabs x and y data. Plots using matplotlib bar plot.
    Saves the file to a temp folder created during module initialization.
    Uploads to imgur.
    """
    data_list = get_db_data(job_dict["start"], job_dict["end"],
                            job_dict["limit"], job_dict["offset"])

    if data_list:
        x_data = [dict_x["year"] for dict_x in data_list]
        y_data = [dict_x["spots"] for dict_x in data_list]

        plt.bar(x_data, y_data)
        plt.title("Sunspots recorded per year")
        plt.xlabel("Year")
        plt.ylabel("Number of Sunspots")

        image_path = GRAPH_DIR + "graph_" + job_dict["id"] + ".png"
        plt.savefig(image_path)

        imgur_link = imgur_upload(image_path)
    return imgur_link


def imgur_upload(image_path):
    """
    Takes the temporary path to an plotted image.
    Reads in image, converts to bytes, and post to imgur using an api.imgur post.
    Returns imgur link as results.
    """
    with open(image_path, "rb") as image_file:
        image_smaller = image_file.read()
        byte_image = bytearray(image_smaller)

    imgur_req = r.post("https://api.imgur.com/3/image", byte_image,
                       headers={'Authorization':'Client-ID 8af4e56496131e0'})

    return imgur_req.json()['data']['link']


if __name__ == "__main__":
    # Creates a temporary folder for plots if it does not exist.
    CODE_DIR = os.path.join(os.path.dirname(__file__), '')
    GRAPH_DIR = CODE_DIR + "../temp_graphs/"
    if not os.path.exists(GRAPH_DIR):
        os.mkdir(GRAPH_DIR)
    print("Graph worker running")
    graph_worker()
