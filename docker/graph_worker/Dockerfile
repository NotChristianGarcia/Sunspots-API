FROM python:3.7-slim
WORKDIR /graph_worker
ADD /src/graph_worker.py /src/jobs.py /src/get_db_data.py ./
RUN pip3 install requests redis hotqueue matplotlib
CMD ["python3", "graph_worker.py"]
