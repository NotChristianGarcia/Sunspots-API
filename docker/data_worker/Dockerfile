FROM python:3.7-alpine
WORKDIR /data_worker
ADD /src/data_worker.py /src/jobs.py /src/get_db_data.py ./
RUN pip3 install redis hotqueue
CMD ["python3", "data_worker.py"]
