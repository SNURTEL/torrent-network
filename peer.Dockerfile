FROM python:3.11-alpine

ARG COMMAND
ENV command=$COMMAND

RUN apk --upgrade add iptables iproute2

RUN mkdir /code
COPY src /code/src
WORKDIR /code/src/peer
ENV PYTHONPATH="${PYTHONPATH}:/code"

ENTRYPOINT sleep 1 && sh -c "tc qdisc add dev eth0 root netem delay 5ms" && python3 -u peer.py $command