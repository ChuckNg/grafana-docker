#!/bin/bash
DIRNAME=$(readlink -f `dirname $0`)
REPO=""
TAG="1.0.0"

cd $DIRNAME

echo "=== Building..."
docker build -t $REPO/grafana:$TAG .

echo "=== Pusing..."
docker push $REPO/grafana:$TAG
