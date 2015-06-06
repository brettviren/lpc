#!/bin/bash

crossbar start > crossbar.log 2>&1 &
crossbar_pid=$!
echo crossbar.log

sleep 1

python lpc/service.py > service.log 2>&1 &
service_pid=$!
echo service.log

sleep 1

python lpc/client.py

kill $service_pid
kill $crossbar_pid
