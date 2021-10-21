#!/usr/bin/env bash
docker run -ti \
    --net=host \
    -e SECRET_KEY=verysecure \
    -e FLASK_APP=flaskwebmapsandbox \
    -e FLASK_ENV=dev \
    "flask-webmap-sandbox:latest" \
    "$@"