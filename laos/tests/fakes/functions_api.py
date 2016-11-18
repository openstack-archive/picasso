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

import collections
import uuid

from functionsclient import client
from functionsclient.v1 import apps
from functionsclient.v1 import routes


APPS = dict()
APP_ROUTES = collections.defaultdict(list)


class FakeRoutes(object):

    def __init__(self, app_name):
        self.app_name = app_name

    async def list(self, loop=None):
        return APP_ROUTES[self.app_name]

    async def create(self, loop=None, **data):
        app_routes = APP_ROUTES[self.app_name]
        if data.get("path") in [route.path for route in app_routes]:
            raise client.FunctionsAPIException(
                "App {} route {} already exists.".format(
                    self.app_name, data.get("path")), 409)
        else:
            data.update(
                appname=self.app_name,
                memory=256
            )
            _route = routes.AppRouteResource(**data)
            APP_ROUTES[self.app_name].append(_route)
            return _route

    async def show(self, path, loop=None):
        app_routes = APP_ROUTES[self.app_name]
        for route in app_routes:
            if path == route.path:
                return route
        raise client.FunctionsAPIException(
            "App {} route {} not found.".format(
                self.app_name, path), 404)

    async def delete(self, path, loop=None):
        app_routes = APP_ROUTES[self.app_name]
        if path not in [route.path for route in app_routes]:
            raise client.FunctionsAPIException(
                "App {} route {} not found.".format(
                    self.app_name, path), 404)
        else:
            app_routes.pop(
                app_routes.index(
                    await self.show(path, loop=loop)
                )
            )

    async def execute(self, path, loop=None):
        app_routes = APP_ROUTES[self.app_name]
        if path not in [route.path for route in app_routes]:
            raise client.FunctionsAPIException(
                "App {} route {} not found.".format(
                    self.app_name, path), 404)
        else:
            route = await self.show(path)
            return "Hello world!" if route.type == "sync" else {
                "call_id": uuid.uuid4().hex
            }


class FakeApps(object):

    def __init__(self):
        pass

    async def list(self, loop=None):
        return list(APPS.values())

    async def create(self, app_name, loop=None):
        if app_name not in APPS:
            _app = apps.AppResource(
                FakeRoutes(app_name),
                **{"name": app_name, "config": None})
            APPS.update({app_name: _app})
            return _app
        else:
            raise client.FunctionsAPIException(
                "App {} already exist".format(app_name), 409)

    async def show(self, app_name, loop=None):
        if app_name not in APPS:
            raise client.FunctionsAPIException(
                "App {} already exist.".format(app_name), 404)
        else:
            return APPS.get(app_name)

    async def delete(self, app_name, loop=None):
        if app_name not in APPS:
            raise client.FunctionsAPIException(
                "App {} already exist.".format(app_name), 404)
        else:
            del APPS[app_name]


class FunctionsAPIV1(object):

    def __init__(self, *args, **kwargs):
        self.apps = FakeApps()
