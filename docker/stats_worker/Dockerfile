FROM python:3.7-alpine
WORKDIR /stats_worker
ADD /src/stats_worker.py /src/jobs.py /src/get_db_data.py ./
RUN pip3 install redis hotqueue
CMD ["python3", "stats_worker.py"]
