#!/usr/bin/env bash

set +x
set +e
set +i

docker build -t picasso-api -f Dockerfile . 2>&1
docker_h=$(echo ${DOCKER_HOST} | tr "://" " " |awk '{print $2}')
echo -e "Docker IP address ${docker_h}"
echo -e "OpenStack Identity service URL ${OS_AUTH_URL}"
echo -e "IronFunctions URL ${FUNCTIONS_API_URL}"
echo -e "Persistent storage URI ${TEST_DB_URI}"
docker run -d -p ${docker_h}:10002:10001 --env PICASSO_HOST=0.0.0.0 --env PICASSO_PORT=10001 --env PICASSO_DB=${TEST_DB_URI} --env KEYSTONE_ENDPOINT=${OS_AUTH_URL} --env FUNCTIONS_URL=${FUNCTIONS_API_URL} --env PICASSO_LOG_LEVEL=INFO picasso-api
sleep 2
docker ps
echo -e "Service running on ${docker_h}:10002"
curl -X GET http://${docker_h}:10002/api/swagger.json | python -mjson.tool
docker stop -t 1 $(docker ps | grep "${docker_h}:10002" | awk '{print $1}')
