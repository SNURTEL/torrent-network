#!/bin/sh
tc qdisc add dev eth0 root netem delay 200ms 100ms loss 25%
python3 server.py
