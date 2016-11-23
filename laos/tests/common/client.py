# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import json as jsonlib

from aiohttp import test_utils


class AppsV1(object):

    # /v1/{project_id}/apps
    apps_path = "/v1/{}/apps"
    # /v1/{project_id}/apps/{app}
    app_path = apps_path + "/{}"

    def __init__(self, test_client):
        self.client = test_client

    async def list(self):
        return await self.client.list(self.apps_path)

    async def show(self, app_name):
        return await self.client.show(self.app_path, app_name)

    async def create(self, app_name):
        data = {
            "app": {
                "name": app_name
            }
        }
        return await self.client.create(self.apps_path, data)

    async def delete(self, app_name):
        return await self.client.remove(self.app_path, app_name)


class RoutesV1(object):

    # /v1/{project_id}/apps/{app}/routes
    routes_path = "/v1/{}/apps/{}/routes"
    # /v1/{project_id}/apps/{app}/routes{}
    route_path = routes_path + "{}"

    def __init__(self, test_client):
        self.client = test_client

    async def list(self, app_name):
        return await self.client.list(
            self.routes_path, app_name)

    async def show(self, app_name, path):
        return await self.client.show(
            self.route_path, app_name, path)

    async def create(self, app_name, **data):
        return await self.client.create(
            self.routes_path, {"route": data}, app_name)

    async def delete(self, app_name, path):
        return await self.client.remove(
            self.route_path, app_name, path)


class ProjectBoundLaosTestClient(test_utils.TestClient):

    def __init__(self, app_or_server, project_id, **kwargs):
        super(ProjectBoundLaosTestClient, self).__init__(app_or_server)
        self.project_id = project_id
        self.headers = {
            "Content-Type": "application/json"
        }
        if kwargs.get("headers"):
            self.headers.update(kwargs.get("headers"))

        self.apps = AppsV1(self)
        self.routes = RoutesV1(self)

    async def create(self, route, data, *parts):
        resp = await self.post(
            route.format(self.project_id, *parts),
            data=jsonlib.dumps(data), headers=self.headers)
        json = await resp.json()
        return json, resp.status

    async def list(self, route, *parts):
        resp = await self.get(
            route.format(self.project_id, *parts),
            headers=self.headers)
        json = await resp.json()
        return json, resp.status

    async def show(self, route, resource_name, *parts):
        resp = await self.get(
            route.format(self.project_id, resource_name, *parts),
            headers=self.headers)
        json = await resp.json()
        return json, resp.status

    async def remove(self, route, resource_name, *parts):
        resp = await  self.delete(
            route.format(self.project_id, resource_name, *parts),
            headers=self.headers)
        json = await resp.json()
        return json, resp.status
