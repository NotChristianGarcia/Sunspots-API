
## Sunspots API Documentation
---
These are the specifications to my Sunspots API. Examples are listed for all endpoints. Usage with curl is shown for each example. A short example using requests is at the bottom of the specs. Just convert curl calls to requests to do everything using requests if you want (That is too much to type for me. Sorry.).

---
## Endpoints
These are the possible endpoints to my API. 
By default you can access the API using port 5000, and host as localhost if you're on that VM. Otherwise find the IP of the API VM and access the API using "http://vm-ip:5000." This will be shortened to http://example for simplicity throughout the following examples.

---
### GET /spots?start=<start\>&end=<end\>&limit=<limit\>&offset=<offset\>
Takes inputs and returns the correct JSON list of datapoint dictionaries that match your bounds.
#### Inputs:

	Start: Must be postive Int
	End: Must be positive Int
	Limit: Must be positive Int
	Offset: Must be postitive Int
	
	*Start or end must be used independently of limit or offset

#### Returns:

	On Success: Returns JSON list of requested datapoint dictionaries
	On Failure: Returns JSON list of input errors
	
#### Examples
##### No parameters -
	$ curl "http://example/spots"
	[{"id": 0, "spots": 101, "year": 1770},
	 {'id': 1, 'spots': 82, 'year': 1771},
	 ...]
Returns a JSON list of all datapoints in the dataset.

##### Start parameter
	$ curl "http://example/spots?start=1822"
	[{"id": 52, "spots": 4, "year": 1822},
	 {'id': 53, 'spots': 2, 'year': 1823},
	 ...]
Returns a JSON list of every datapoint with year 1822 and beyond.

##### End parameter
	$ curl "http://example/spots?end=1840"
	[...,
	 {"id": 69, "spots": 86, "year": 1839},
	 {'id': 70, 'spots': 65, 'year': 1840}]
Returns a JSON list of every datapoint up to and including the year 1840.

##### Limit parameter
	$ curl "http://example/spots?limit=17"
	[{"id": 0, "spots": 101, "year": 1770},
	 ...
	 {'id': 16, 'spots': 83, 'year': 1786}]
Returns a JSON list of 17 datapoints starting from the first datapoint in the dataset.

##### Offset parameter
	$ curl "http://example/spots?offset=78"
	[{"id": 78, "spots": 125, "year": 1848},
	 {'id': 79, 'spots': 96, 'year': 1849},
	 ...]
Returns a JSON list of every datapoint after datapoint 78 in the dataset.

##### Parameter combinations 
	$ curl "http://example/spots?start=1860&end=1866"
	[{"id": 90, "spots": 125, "year": 1860},
	 ...
	 {'id': 96, 'spots': 16, 'year': 1866}]
Returns a JSON list of every datapoint with year between and including 1860 to 1866.

	$ curl "http://example/spots?limit=19&offset=4"
	[{"id": 4 "spots": 31, "year": 1774},
	 ...
	 {'id': 22, 'spots': 60, 'year': 1792}]
Returns a JSON list of 19 datapoints starting from and including datapoint 4.

	$ curl "http://example/spots?start=1920&limit=2"
	['Start and end can only be used independently from limit and offset.']
Returns a JSON list of errors, including a string stating that start or end must be ran independently of limit or offset.

---
### POST /spots
Takes a JSON list of datapoint dictionaries and add it's to the dataset.
#### Inputs:

	Payload: JSON list of datapoint dictionaries
		- Each dictionary must contain 'year' and 'spots' key
		- 'ID' will be taken, but will get thrown out during sort

#### Returns:

	On Success: Returns JSON string to confirm your additions went through
	On Failure: Returns JSON string of your error
	
#### Examples:

	$ curl --data '[{"spots": 4, "year": 2006}]' "http://example/spots"
	"Your additions went through!"
Returns a JSON string stating if additions went through.

---
### GET /spots/years/<year\>
Takes year input and returns the JSON dictionary corresponding to that input.
#### Inputs:

	Year: Must be positive Int

#### Returns:

	On Success: Returns JSON dict of requested datapoint
	On Failure: Returns JSON list of input errors
	
#### Examples:

	$ curl "http://example/spots/years/1790"
	{"id": 20 "spots": 90, "year": 1790}
Returns the JSON dictionary of information pertaining to the inputted year.

---
### GET /spots/ids/<id\>
Takes ID input and returns the JSON dictionary corresponding to that input.
#### Inputs:

	ID: Must be positive Int

#### Returns:

	On Success: Returns JSON dict of requested datapoint
	On Failure: Returns JSON list of input errors
#### Examples:

	$ curl "http://example/spots/ids/17"
	{"id": 17 "spots": 132, "year": 1787}
Returns the JSON dictionary of information pertaining to the inputted id.

---
### POST /jobs/<job_type/> or /jobs
Takes a JSON dict of parameters and queues jobs according to that.
#### Inputs:

	Job_Type: Either "data", "graph", or "stats"
		- If none given and you use /jobs, data job will be submitted

	Payload: JSON dict of parameters
		- Parameters
			- Start: Must be postive Int
			- End: Must be postive Int
			- Limit: Must be positive Int
			- Offset: Must be positive Int
#### Returns:

	On Success: Returns JSON dict of job
	On Failure: Returns JSON list of input errors
#### Examples:
	$ curl --data '{"start": 1700, "end": 1800}' "http://example/jobs/graph"
	{'end': 1870,
	 'id': '97b35542-f63e-47f0-88e0-33195a2abbaf',
	 'limit': None,
	 'offset': None,
	 'results': '',
	 'start': 1790,
	 'start time': '2018-12-13 19:27:41.054159',
	 'status': 'Submitted',
	 'updated time': '2018-12-13 19:27:41.054159',
	 'work type': 'data'}

Returns the JSON dictionary corresponding to your created job.

---
### GET /jobs
Returns all job dictionaries in a JSON list.
#### Returns:

	On Success: Returns JSON list of all job dictionaries
#### Examples:
	$ curl "http://example/jobs"
	[{'end': 1870,
	  'id': '2abbc18c-9a44-4c1d-a10a-5e58c1332476',
	  'limit': None,
	  'offset': None,
	  'results': '',
	  'start': 1790,
	  'start time': '2018-12-13 19:39:39.645808',
	  'status': 'Submitted',
	  'updated time': '2018-12-13 19:39:39.645808',
	  'work type': 'stats'},
	  ...
	 {'end': 1870,
	  'id': '380e635d-bb63-4fa0-8254-86cce3063c07',
	  'limit': None,
	  'offset': None,
	  'results': 'https://i.imgur.com/sVr7tPx.png',
	  'start': 1790,
	  'start time': '2018-12-13 05:28:14.289795',
	  'status': 'Completed',
	  'updated time': '2018-12-13 05:28:15.719587',
	  'work type': 'graph'}]

Returns a JSON list of all job dictionaries in JOB_DB.

---
### GET /jobs/<job_id\>
Returns job dictionary corresponding to job_id.
#### Inputs:

	Job_ID: Must be a correct Job_ID
#### Returns:

	On Success: Returns JSON dict of job corresponding to Job_ID
	On Failure: Returns JSON string stating that Job_ID was not found
#### Examples:
	$ curl "http://example/jobs/380e635d-bb63-4fa0-8254-86cce3063c07"
	{'end': 1870,
	 'id': '380e635d-bb63-4fa0-8254-86cce3063c07',
	 'limit': None,
	 'offset': None,
	 'results': 'https://i.imgur.com/sVr7tPx.png',
	 'start': 1790,
	 'start time': '2018-12-13 05:28:14.289795',
	 'status': 'Completed',
	 'updated time': '2018-12-13 05:28:15.719587',
	 'work type': 'graph'},

Returns a JSON dictionary corresponding to the inputted Job_ID.

---
### GET /jobs/<job_id\>/results
Returns jsonified results for the given job_id.
#### Inputs:

	Job_ID: Must be a correct Job_ID
#### Returns:

	On Success: Returns jsonified results for the given Job_ID
	On Failure: Returns JSON string stating that Job_ID was not found
				Returns JSON string stating that job is not yet completed
#### Examples:
	$ curl "http://example/jobs/380e635d-bb63-4fa0-8254-86cce3063c07/results"
	'https://i.imgur.com/sVr7tPx.png'
Returns a jsonified version of job results.

---
## Examples

---
### Curl
	$ curl "http:/localhost:5000/spots?start=1820&end=1821"
	[{"id": 50, "spots": 16, "year": 1820},
	 ...
	 {'id': 51, 'spots': 7, 'year': 1821},]
---
### Requests with Python
	$ ipython3
    [1] import requests as r
    [2] res = r.get("http:/localhost:5000/spots?start=1820&end=1821")
    [3] res
    <Response [200]>
    [4] res.json()
    [{"id": 50,"spots": 16,"year": 1820},{"id": 51,"spots": 7,"year": 1821}]

---
## Charge Structure
For a basic data-oriented API like this we could allow 8 gets to the server per day. Post and more gets would come with a one-time fee. This means that our data can be used by many new people and they could see the worth of the data and API. Students and other third-parties would be able to raise publicity with their use of the API. For users that need added functionality or just more use, the user can pay the one-time fee so the users feels compelled to continue using the product, again raising publicity. To enforce these usage limits any access to the API would require a login from a setup account. Post would be limited only due to the fact that users in most cases wouldn't have any need in accessing any jobs or adding data. If they do need this access then payment would be neccessary as a way to raise funds for server cost.
