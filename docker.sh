#!/bin/bash

# -it python:3.7-slim python3 -m http.server --bind 0.0.0.0 --name Logos davidhaase/logos  
docker build --build-arg BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ') -t davidhaase/logos .
docker container run -d -p 5000:5000 --name Logos davidhaase/logos  