FROM python:3.11-alpine

RUN mkdir /code
COPY . /code/project
WORKDIR /code/project
ENV PYTHONPATH="${PYTHONPATH}:/code"

ENTRYPOINT ["python3","-u", "coordinator/coordinator.py"]