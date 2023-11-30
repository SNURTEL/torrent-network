#!/bin/sh
tc qdisc add dev eth0 root netem delay 200ms 100ms loss 50%
python3 server.py
