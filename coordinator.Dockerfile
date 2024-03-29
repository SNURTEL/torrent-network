FROM python:3.11-alpine

RUN apk --upgrade add iptables iproute2

RUN mkdir /code
COPY src /code/src
WORKDIR /code/src
ENV PYTHONPATH="${PYTHONPATH}:/code"

ENTRYPOINT sh -c "tc qdisc add dev eth0 root netem delay 5ms" && python3 -u coordinator/coordinator.py