FROM python:3.11-alpine

ARG ADDR
ENV addr=$ADDR

RUN apk --upgrade add iptables iproute2

RUN mkdir /code
COPY . /code/project
WORKDIR /code/project/peer
ENV PYTHONPATH="${PYTHONPATH}:/code"

ENTRYPOINT sh -c "tc qdisc add dev eth0 root netem delay 5ms" && python3 -u peer_server.py $addr