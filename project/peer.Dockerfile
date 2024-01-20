FROM python:3.11-alpine

RUN mkdir /code
COPY . /code/project
WORKDIR /code/project/peer
ENV PYTHONPATH="${PYTHONPATH}:/code"

ENTRYPOINT ["python3","-u", "peer.py"]