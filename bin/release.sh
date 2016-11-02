#!/bin/bash
set -ex

USERNAME=askhatomarov
IMAGE=happ

bumpversion $1 --allow-dirty
version=`cat VERSION`
echo "version: $version"

./bin/build.sh

git add .
git commit -m "version $version"
git tag -a "$version" -m "version $version"
git push origin master
git push --tags

docker tag $USERNAME/$IMAGE:latest $USERNAME/$IMAGE:$version

docker push $USERNAME/$IMAGE:latest
docker push $USERNAME/$IMAGE:$version
