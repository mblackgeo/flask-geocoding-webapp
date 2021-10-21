#!/usr/bin/env bash
set -x
echo "Running at : http://localhost:5000/"
docker run -ti \
    --net=host \
    -e SECRET_KEY=verysecure \
    -e FLASK_APP=flaskwebmapsandbox \
    -e FLASK_ENV=dev \
    "flask-webmap-sandbox:latest" \
    "$@"
