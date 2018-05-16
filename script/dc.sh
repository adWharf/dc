#!/usr/bin/env bash

docker stop dc;
docker rm dc;
docker build -t dc .;
docker run --name dc --network dc --network-alias dc -d dc
