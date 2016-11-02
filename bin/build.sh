#!/bin/bash
set -ex

USERNAME=askhatomarov
IMAGE=happ

docker build -t $USERNAME/$IMAGE:latest .
