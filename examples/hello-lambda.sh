#!/usr/bin/env bash

set +x
set +e

export LAOS_API_URL=${LAOS_API_URL:-http://localhost:10001}

export OS_AUTH_URL=${OS_AUTH_URL:-http://localhost:5000/v3}
export OS_USERNAME=${OS_USERNAME:-admin}
export OS_PASSOWRD=${OS_PASSWORD:-root}
export OS_DOMAIN=${OS_DOMAIN:-default}
export OS_PROJECT_ID=${OS_PROJECT_ID:-"dummy_project_id"}


rm -fr examples/token_request.json
echo -e "{
  \"auth\": {
    \"identity\": {
      \"methods\": [\"password\"],
      \"password\": {
        \"user\": {
          \"name\": \"${OS_USERNAME:-admin}\",
          \"domain\": { \"id\": \"${OS_DOMAIN:-default}\" },
          \"password\": \"${OS_PASSWORD:-root}\"
        }
      }
    },
    \"scope\": {
      \"project\": {
        \"name\": \"${OS_PROJECT_NAME:-admin}\",
        \"domain\": {\"id\": \"${OS_DOMAIN:-default}\" }
      }
    }
  }
}" >> examples/token_request.json


export OS_TOKEN=`curl -si -d @examples/token_request.json -H "Content-type: application/json" ${OS_AUTH_URL}/auth/tokens | awk '/X-Subject-Token/ {print $2}'`

echo -e "Listing apps\n"
curl ${LAOS_API_URL}/v1/${OS_PROJECT_ID}/apps -H "X-Auth-Token:${OS_TOKEN}" -H "Content-Type: application/json" | python3 -mjson.tool

echo -e "Creating app\n"
curl -X POST -d '{"app":{"name": "testapp"}}' ${LAOS_API_URL}/v1/${OS_PROJECT_ID}/apps -H "X-Auth-Token:${OS_TOKEN}" -H "Content-Type: application/json" | python3 -mjson.tool

echo -e "Listing apps\n"
curl ${LAOS_API_URL}/v1/${OS_PROJECT_ID}/apps -H "X-Auth-Token:${OS_TOKEN}" -H "Content-Type: application/json" | python3 -mjson.tool

echo -e "Showing app info\n"
export raw_app_info=`curl localhost:10001/v1/${OS_PROJECT_ID}/apps -H "X-Auth-Token:${OS_TOKEN}" -H "Content-Type: application/json" | python3 -mjson.tool | grep name | awk '{print $2}'`
export app_name=${raw_app_info:1:30}
curl ${LAOS_API_URL}/v1/${OS_PROJECT_ID}/apps/${app_name} -H "X-Auth-Token:${OS_TOKEN}" -H "Content-Type: application/json" | python3 -mjson.tool

echo -e "Listing app routes\n"
curl ${LAOS_API_URL}/v1/${OS_PROJECT_ID}/apps/${app_name}/routes -H "X-Auth-Token:${OS_TOKEN}" -H "Content-Type: application/json" | python3 -mjson.tool

echo -e "Creating app sync private route\n"
curl -X POST -d '{"route":{"type": "sync", "path": "/hello-sync-private", "image": "iron/hello", "is_public": "false" }}' ${LAOS_API_URL}/v1/${OS_PROJECT_ID}/apps/${APP_NAME}/routes -H "X-Auth-Token:${OS_TOKEN}" -H "Content-Type: application/json" | python3 -mjson.tool

echo -e "Creating app sync public route\n"
curl -X POST -d '{"route":{"type": "sync", "path": "/hello-sync-public", "image": "iron/hello", "is_public": "true" }}' ${LAOS_API_URL}/v1/${OS_PROJECT_ID}/apps/${APP_NAME}/routes -H "X-Auth-Token:${OS_TOKEN}" -H "Content-Type: application/json" | python3 -mjson.tool

echo -e "Listing app routes\n"
curl ${LAOS_API_URL}/v1/${OS_PROJECT_ID}/apps/${app_name}/routes -H "X-Auth-Token:${OS_TOKEN}" -H "Content-Type: application/json" | python3 -mjson.tool

echo -e "Show app private route\n"
curl ${LAOS_API_URL}/v1/${OS_PROJECT_ID}/apps/${app_name}/routes/hello-sync-private -H "X-Auth-Token:${OS_TOKEN}" -H "Content-Type: application/json" | python3 -mjson.tool

echo -e "Show app public route\n"
curl ${LAOS_API_URL}/v1/${OS_PROJECT_ID}/apps/${app_name}/routes/hello-sync-public -H "X-Auth-Token:${OS_TOKEN}" -H "Content-Type: application/json" | python3 -mjson.tool

echo -e "Running app sync private route\n"
curl -X POST -d '{"name": "Johnny"}' ${LAOS_API_URL}/private/${OS_PROJECT_ID}/${app_name}/hello-sync-private -H "X-Auth-Token:${OS_TOKEN}" -H "Content-Type: application/json" | python3 -mjson.tool

echo -e "Running app sync public route\n"
curl -X POST -d '{"name": "Johnny"}' ${LAOS_API_URL}/public/${app_name}/hello-sync-public -H "Content-Type: application/json" | python3 -mjson.tool

echo -e "Creating app async route\n"
curl -X POST -d '{"route":{"type": "async", "path": "/hello-async-private", "image": "iron/hello", "is_public": "false"}}' ${LAOS_API_URL}/v1/${OS_PROJECT_ID}/apps/${app_name}/routes -H "X-Auth-Token:${OS_TOKEN}" -H "Content-Type: application/json" | python3 -mjson.tool

echo -e "Running app async route\n"
curl -X POST -d '{"name": "Johnny"}' ${LAOS_API_URL}/private/${OS_PROJECT_ID}/${app_name}/hello-async-private -H "X-Auth-Token:${OS_TOKEN}" -H "Content-Type: application/json" | python3 -mjson.tool

echo -e "Deleting app route\n"
curl -X DELETE ${LAOS_API_URL}/v1/${OS_PROJECT_ID}/apps/${app_name}/routes/hello-sync-public -H "X-Auth-Token:${OS_TOKEN}" -H "Content-Type: application/json" | python3 -mjson.tool
curl -X DELETE ${LAOS_API_URL}/v1/${OS_PROJECT_ID}/apps/${app_name}/routes/hello-sync-private -H "X-Auth-Token:${OS_TOKEN}" -H "Content-Type: application/json" | python3 -mjson.tool
curl -X DELETE ${LAOS_API_URL}/v1/${OS_PROJECT_ID}/apps/${app_name}/routes/hello-async-private -H "X-Auth-Token:${OS_TOKEN}" -H "Content-Type: application/json" | python3 -mjson.tool

echo -e "Listing app routes\n"
curl ${LAOS_API_URL}/v1/${OS_PROJECT_ID}/apps/${app_name}/routes -H "X-Auth-Token:${OS_TOKEN}" -H "Content-Type: application/json" | python3 -mjson.tool

echo -e "Deleting app\n"
curl -X DELETE ${LAOS_API_URL}/v1/${OS_PROJECT_ID}/apps/${app_name} -H "X-Auth-Token:${OS_TOKEN}" -H "Content-Type: application/json" | python3 -mjson.tool

echo -e "Listing apps\n"
curl ${LAOS_API_URL}/v1/${OS_PROJECT_ID}/apps -H "X-Auth-Token:${OS_TOKEN}" -H "Content-Type: application/json" | python3 -mjson.tool
