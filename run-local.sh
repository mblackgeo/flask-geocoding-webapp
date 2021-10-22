#!/usr/bin/env bash
set -x
echo "Running at : http://localhost:5000/"
docker run -ti \
    --net=host \
    --env-file ./.env \
    "flask-geocoding-webapp:latest" \
    "$@"
