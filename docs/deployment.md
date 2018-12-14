
## Sunspots API Deployment
---
There are three ways to deploy my Sunspots API. On one VM, two VMs, or four VMs.

---
### One Virtual Machine
On one VM, all four docker containers will be ran together.

#### How To: 
To deploy on one VM you have to make no modifications.
##### First, pull repository:

	$ git clone https://notchristiangarcia@bitbucket.org/notchristiangarcia/sunspots-api.git
##### Second, move into "1_machine" deployment directory:
	
	$ cd sunspots-api/deploy/use_images/1_machine/
	or
	$ cd sunspots-api/deploy/local_build/1_machine/
	or
	to build locally
##### Thirdly, docker-compose up to build and run:

	$ docker-compose up
	
---
### Two Virtual Machines
On two VMs, one VM will run the api container, and the other will run all three worker containers.

#### How To:
To deploy on two VM's you will have to do some work.
##### First, on each VM, pull repository:

	$ git clone https://notchristiangarcia@bitbucket.org/notchristiangarcia/sunspots-api.git
##### Second, on each VM, move into "2_machines" deployment directory:
	
	$ cd sunspots-api/deploy/use_images/2_machines/
	or
	$ cd sunspots-api/deploy/local_build/2_machines/
	or
	to build locally
##### Third,  in the worker VM* you must edit, in this directory, worker_vars.env. Using your preferred text editor, change "REDIS_IP" to the 10.* IP address from the VM running the API. 
*You may change the worker_vars.env in both VM's, but it is only necessary on the worker VM.

	$ vim worker_vars.env
		> REDIS_IP=10.endofiphere
##### Fourth, on the first VM running the api, do the following:
*Note: It doesn't matter in which order you "docker-compose up" fail-safes are in play.

	$ docker-compose -f dc-api.yml up

##### Fifth, on the second VM running the workers, do the following:

	$ docker-compose -f dc-workers.yml up
	
---	
### Four Virtual Machines
On four machines, the api container, the data worker container, the graph worker container, and the stats worker container will all run separately on their own VM.

#### How To:
To deploy on four VM's you will have to do some work.
##### First, on each VM, pull repository:

	$ git clone https://notchristiangarcia@bitbucket.org/notchristiangarcia/sunspots-api.git
##### Second, on each VM, move into "4_machines" deployment directory:
	
	$ cd sunspots-api/deploy/use_images/4_machines/
	or
	$ cd sunspots-api/deploy/local_build/4_machines/
	or
	to build locally
##### Third,  in all three worker VMs* you must edit, in this directory, worker_vars.env. Using your preferred text editor, change "REDIS_IP" to the 10.* IP address from the VM running the API.
*You may change the worker_vars.env in all four VM's, but it is only necessary on the worker VMs.

	$ vim worker_vars.env
		> REDIS_IP=10.endofiphere
##### Fourth, on the first VM running the api, do the following:
*Note: It doesn't matter in which order you "docker-compose up" fail-safes are in play.

	$ docker-compose -f dc-api.yml up

##### Fifth, on the second VM running the data worker, do the following:

	$ docker-compose -f dc-data.yml up
##### Sixth, on the third VM running the graph worker, do the following:

	$ docker-compose -f dc-graph.yml up
##### Seventh, on the fourth VM running the stats worker, do the following:

	$ docker-compose -f dc-stats.yml up
