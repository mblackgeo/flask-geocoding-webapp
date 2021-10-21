#!/usr/bin/env bash
docker run -ti \
    --net=host \
    -e ENV='test' \
    "flask-webmap-sandbox:latest" \
    "$@"