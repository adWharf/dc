#!/usr/bin/env bash
docker stop schedule;
docker rm schedule;
docker build -t schedule -f Dockerfile-schedule .;
docker run --name schedule --network dc --network-alias schedule --restart=always -d schedule;
