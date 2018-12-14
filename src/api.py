"""
Author: Christian R. Garcia
Creates a flask server with different routes that allows for calling data,
posting data, and creating jobs based off of the "sunspots.csv" data collection
"""
from time import sleep
import json
from flask import Flask, jsonify, request
import jobs
import file_ops
from get_db_data import get_db_data

app = Flask(__name__)


@app.route('/spots', methods=['GET'])
def get_db_data_with_args():
    """
    Takes a start, end, limit, and offset value from route arguments.
    Checks input with input_checker, returns 400 and errors if they exist.
    Otherwises returns json list of data requested.
    """
    start = request.args.get('start')
    end = request.args.get('end')
    limit = request.args.get('limit')
    offset = request.args.get('offset')

    start, end, limit, offset, errors = input_checker(start, end, limit, offset)
    if errors:
        return jsonify(errors), 400
    data_list = get_db_data(start, end, limit, offset)
    return jsonify(data_list)


@app.route('/spots', methods=['POST'])
def add_dict():
    """
    Takes a json list of dictionaries as a post payload, dictionaries must contain
    'year' and 'spots' keys, will take 'id' if it's provided.
    Takes each dictionary and adds it to the dataset.
    Will not replace data points, just adds next to them.
    """
    post_data = json.loads(request.get_data().decode("utf-8"))
    if isinstance(post_data, list):
        for dict_x in post_data:
            if isinstance(dict_x, dict):
                if not len(dict_x) in [2, 3]:
                    return jsonify("Sorry, your dict may only have keys",
                                   "for 'id', 'year', and 'spots'"), 400
                try:
                    if dict_x['year'] < 0 or not isinstance(dict_x['year'], int):
                        return jsonify("Sorry your value for 'year' must be a postive int"), 400
                except:
                    return jsonify("Sorry, your dicts must have a value for 'year'"), 400
                try:
                    if dict_x['spots'] < 0 or not isinstance(dict_x['spots'], int):
                        return jsonify("Sorry your value for 'spots' must be a postive int"), 400
                except:
                    return jsonify("Sorry, your dicts must have a value for 'spots'"), 400
            else:
                return jsonify("Sorry, your json list had no dicts in it"), 400
    else:
        return jsonify("Sorry, post data must be a json list of dicts"), 400

    file_ops.update_redis_and_csv(post_data)
    return jsonify("Your additions went through!")


@app.route('/spots/ids/<id_input>', methods=['GET'])
def get_id(id_input):
    """
    Takes an id as route argument.
    Checks input with input_checker, returns 400 and errors if they exist.
    Returns data point dictionary corresponding to id.
    """
    start, end, limit, offset, errors = input_checker(id_input=id_input)
    if errors:
        return jsonify(errors), 400
    data_list = get_db_data(start, end, limit, offset)
    return jsonify(data_list[0])


@app.route('/spots/years/<year>', methods=['GET'])
def get_year(year):
    """
    Takes a year as route argument.
    Checks input with input_checker, returns 400 and errors if they exist.
    Returns data point dictionary corresponding to year.
    """
    start, end, limit, offset, errors = input_checker(year=year)
    if errors:
        return jsonify(errors), 400
    data_list = get_db_data(start, end, limit, offset)
    return jsonify(data_list[0])

@app.route('/jobs', methods=['POST'])
@app.route('/jobs/<job_type>', methods=['POST'])
def job_creation(job_type="data"):
    """
    Takes a json dictionary with start, end, limit, or offset keys.
    Checks input with input_checker, returns 400 and errors if they exist.
    'job_type' may be 'stats', 'graph', or 'data'.
    If none given at /jobs post, a data job will be default.
    Submits jobs to job database for use with worker queues.
    Returns job details as json dictionary.
    """
    post_data = json.loads(request.get_data().decode("utf-8"))
    if post_data:
        if "start" in post_data:
            start = post_data["start"]
        else:
            start = None

        if "end" in post_data:
            end = post_data["end"]
        else:
            end = None

        if "limit" in post_data:
            limit = post_data["limit"]
        else:
            limit = None

        if "offset" in post_data:
            offset = post_data["offset"]
        else:
            offset = None

    start, end, limit, offset, errors = input_checker(start, end, limit, offset)
    if errors:
        return jsonify(errors), 400
    return jobs.add_job(job_type, start, end, limit, offset) + "\n"


@app.route('/jobs', methods=['GET'])
def get_all_jobs():
    """
    Returns all jobs in jobs database as json list of dictionaries.
    """
    return jsonify(jobs.get_all_jobs())


@app.route('/jobs/<job_id>', methods=['GET'])
def get_one_job(job_id):
    """
    Checks validity of job_id, if non-valid a 400 error will be returned.
    Returns job dictionary corresponding to job_id if valid.
    """
    try:
        result = jobs.get_job(job_id)
    except:
        return jsonify("Job id supplied led to no hits in our database, please try again."), 400
    return jsonify(result)


@app.route('/jobs/<job_id>/results', methods=['GET'])
def get_job_results(job_id):
    """
    Checks validity of job_id, if non-valid a 400 error will be returned.
    Returns job results corresponding to job_id if valid.
    """
    try:
        results = jobs.get_job(job_id)["results"]
        if not results:
            return jsonify("Your job is not yet completed.")
    except:
        return jsonify("Job id supplied led to no hits in our database, please try again."), 400
    return jsonify(results)


def input_checker(start=None, end=None, limit=None, offset=None, **special_flags):
    """
    Checks inputs for multiple functions.
    Checks for negative inputs, correct types,
    start or end independence of limit or offset.
    Also results correct get_db_data inputs for id_input and year input.
    """
    input_errors = []
    if start is not None:
        try:
            start = int(start)
            if start < 0:
                input_errors.append("Input for 'start' must be positive or 0")
        except ValueError:
            input_errors.append("Input for 'start' must be an int")

    if end is not None:
        try:
            end = int(end)
            if end < 0:
                input_errors.append("Input for 'end' must be positive or 0")
        except ValueError:
            input_errors.append("Input for 'end' must be an int")

    if start is not None and end is not None:
        if start > end:
            input_errors.append("'start' input cannot be larger than 'end'")

    if limit is not None:
        try:
            limit = int(limit)
            if limit < 0:
                input_errors.append("Input for 'limit' must be positive or 0")
        except ValueError:
            input_errors.append("Input for 'limit' must be an int")

    if offset is not None:
        try:
            offset = int(offset)
            if offset < 0:
                input_errors.append("Input for 'offset' must be positive or 0")
        except ValueError:
            input_errors.append("Input for 'offset' must be an int")

    if (start is not None or end is not None) and (limit is not None or offset is not None):
        input_errors.append("Start or end must be used independently of limit or offset")

    if "id_input" in special_flags:
        try:
            id_input = int(special_flags["id_input"])
            if id_input < 0:
                input_errors.append("Input for 'id' must be positive or 0")
            limit = 1
            offset = id_input
        except ValueError:
            input_errors.append("Input for 'id' must be an int")

    if "year" in special_flags:
        try:
            year = int(special_flags["year"])
            if year < 0:
                input_errors.append("Input for 'year' must be positive or 0")
            start = year
            end = year
        except ValueError:
            input_errors.append("Input for 'year' must be an int")

    if input_errors:
        return start, end, limit, offset, input_errors

    return start, end, limit, offset, input_errors


if __name__ == "__main__":
    # Waits for db initialization to be success with running redis.
    while True:
        try:
            file_ops.init_db_data()
            break
        except:
            print("Error: Redis not yet initialized. Reattempting reconnection in 3 seconds")
            sleep(3)
    app.run(debug=False, host='0.0.0.0')