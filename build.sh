#!/usr/bin/env bash
docker build -f Dockerfile -t "flask-geocoding-webapp:latest" $@ .