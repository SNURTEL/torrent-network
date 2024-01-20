FROM python:3.11-alpine

ARG ADDR
ENV addr=$ADDR

RUN mkdir /code
COPY . /code/project
WORKDIR /code/project/peer
ENV PYTHONPATH="${PYTHONPATH}:/code"

ENTRYPOINT python -u dummy_server.py $addr