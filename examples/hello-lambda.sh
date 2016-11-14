#!/usr/bin/env bash

set +x

export LAOS_API_URL=${LAOS_API_URL:-http://localhost:10001}

export OS_AUTH_URL=${OS_AUTH_URL:-http://localhost:5000/v3}
export OS_PROJECT_ID=${OS_PROJECT_ID:-"dummy_project_id"}
export OS_TOKEN=`curl -si -d @token_request.json -H "Content-type: application/json" ${OS_AUTH_URL}/auth/tokens | awk '/X-Subject-Token/ {print $2}'`

echo -e "Listing apps\n"
curl ${LAOS_API_URL}/v1/${OS_PROJECT_ID}/apps -H "X-Auth-Token:${OS_TOKEN}" -H "Content-Type: application/json" | python3 -mjson.tool

echo -e "Creating app\n"
curl -X POST -d '{"app":{"name": "testapp"}}' ${LAOS_API_URL}/v1/${PROJECT_ID}/apps -H "X-Auth-Token:${OS_TOKEN}" -H "Content-Type: application/json" | python3 -mjson.tool

echo -e "Listing apps\n"
curl ${LAOS_API_URL}/v1/${OS_PROJECT_ID}/apps -H "X-Auth-Token:${OS_TOKEN}" -H "Content-Type: application/json" | python3 -mjson.tool

echo -e "Showing app info\n"
export raw_app_info=`curl localhost:10001/v1/${OS_PROJECT_ID}/apps -H "X-Auth-Token:${OS_TOKEN}" -H "Content-Type: application/json" | python3 -mjson.tool | grep name | awk '{print $2}'`
export app_name=${raw_app_info:1:30}
unset $raw_app_info
curl ${LAOS_API_URL}/v1/${OS_PROJECT_ID}/apps/${app_name} -H "X-Auth-Token:${OS_TOKEN}" -H "Content-Type: application/json" | python3 -mjson.tool

echo -e "Listing app routes\n"
curl ${LAOS_API_URL}/v1/${PROJECT_ID}/apps/${APP_NAME}/routes -H "X-Auth-Token:${OS_TOKEN}" -H "Content-Type: application/json" | python3 -mjson.tool

echo -e "Creating app sync route\n"
curl -X POST -d '{"route":{"type": "sync", "path": "/hello-sync", "image": "iron/hello"}}' ${LAOS_API_URL}/v1/${PROJECT_ID}/apps/${APP_NAME}/route -H "X-Auth-Token:${OS_TOKEN}" -H "Content-Type: application/json"

echo -e "Listing app routes\n"
curl ${LAOS_API_URL}/v1/${PROJECT_ID}/apps/${APP_NAME}/routes -H "X-Auth-Token:${OS_TOKEN}" -H "Content-Type: application/json" | python3 -mjson.tool

echo -e "Show app route\n"
curl ${LAOS_API_URL}/v1/${PROJECT_ID}/apps/${APP_NAME}/routes/hello-sync -H "X-Auth-Token:${OS_TOKEN}" -H "Content-Type: application/json" | python3 -mjson.tool

echo -e "Running app sync route\n"
curl -X POST -d '{"name": "Johnny"}' ${LAOS_API_URL}/r/${PROJECT_ID}/${APP_NAME}/hello-sync -H "X-Auth-Token:${OS_TOKEN}" -H "Content-Type: application/json" | python3 -mjson.tool

echo -e "Deleting app route\n"
curl -X DELETE ${LAOS_API_URL}/v1/${PROJECT_ID}/apps/${APP_NAME}/routes/hello_sync -H "X-Auth-Token:${OS_TOKEN}" -H "Content-Type: application/json" | python3 -mjson.tool

echo -e "Creating app async route\n"
curl -X POST -d '{"route":{"type": "async", "path": "/hello-async", "image": "iron/hello"}}' ${LAOS_API_URL}/v1/${PROJECT_ID}/apps/${APP_NAME}/route -H "X-Auth-Token:${OS_TOKEN}" -H "Content-Type: application/json" | python3 -mjson.tool

echo -e "Running app async route\n"
curl -X POST -d '{"name": "Johnny"}' ${LAOS_API_URL}/r/${PROJECT_ID}/${APP_NAME}/hello-async -H "X-Auth-Token:${OS_TOKEN}" -H "Content-Type: application/json" | python3 -mjson.tool

echo -e "Deleting app\n"
curl -X DELETE ${LAOS_API_URL}/v1/${OS_PROJECT_ID}/apps/${app_name} -H "X-Auth-Token:${OS_TOKEN}" -H "Content-Type: application/json" | python3 -mjson.tool
