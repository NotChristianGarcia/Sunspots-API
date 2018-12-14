FROM python:3.7-alpine
WORKDIR /api
COPY /src/api.py /src/get_db_data.py /src/jobs.py /src/file_ops.py /src/sunspots.csv ./
RUN pip3 install flask redis hotqueue uuid
CMD ["python3", "api.py"]
