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

import json

from aiohttp import web

from aioservice.http import controller
from aioservice.http import requests

from laos.api.views import app as app_view
from laos.common import config
from laos.models import app as app_model


class AppRouteV1Controller(controller.ServiceController):

    controller_name = "routes"
    version = "v1"

    @requests.api_action(
        method='GET', route='{project_id}/apps/{app}/routes')
    async def list(self, request, **kwargs):
        """
        ---
        description: Listing project-scoped app routes
        tags:
        - Routes
        produces:
        - application/json
        responses:
            "200":
                description: Successful operation. Return "routes" JSON
            "401":
                description: Not authorized.
            "404":
                description: App does not exist
        """
        c = config.Config.config_instance()
        log, fnclient = c.logger, c.functions_client
        project_id = request.match_info.get('project_id')
        app = request.match_info.get('app')

        log.info("Listing app {} routes for project: {}."
                 .format(app, project_id))

        if not (await app_model.Apps.exists(app, project_id)):
            return web.json_response(data={
                "error": {
                    "message": "App {0} not found".format(app),
                }
            }, status=404)

        fn_app_routes = (await (await fnclient.apps.show(
            app, loop=c.event_loop)).routes.list(loop=c.event_loop))

        for fn_route in fn_app_routes:
            stored_route = (await app_model.Routes.find_by(
                app_name=app,
                project_id=project_id,
                path=fn_route.path)).pop()
            setattr(fn_route, "is_public", stored_route.public)

        api_url = "{}://{}".format(request.scheme, request.host)
        log.info("Listing app {} routes for project: {}."
                 .format(app, project_id))
        return web.json_response(data={
            "routes": app_view.AppRouteView(api_url,
                                            project_id,
                                            fn_app_routes).view(),
            "message": "Successfully loaded app routes",
        }, status=200)

    @requests.api_action(
        method='POST', route='{project_id}/apps/{app}/routes')
    async def create(self, request, **kwargs):
        """
        ---
        description: Creating project-scoped app route
        tags:
        - Routes
        produces:
        - application/json
        parameters:
        - in: body
          name: route
          description: Created project-scoped app
          required: true
          schema:
            type: object
            properties:
              type:
                type: string
              path:
                type: string
              image:
                type: string
              is_public:
                type: boolean
        responses:
            "200":
                description: Successful operation. Return "route" JSON
            "401":
                description: Not authorized.
            "404":
                description: App does not exist
            "409":
                description: App route exists
        """
        c = config.Config.config_instance()
        log, fnclient = c.logger, c.functions_client
        project_id = request.match_info.get('project_id')
        app = request.match_info.get('app')

        if not (await app_model.Apps.exists(app, project_id)):
            return web.json_response(data={
                "error": {
                    "message": "App {0} not found".format(app),
                }
            }, status=404)

        data = (await request.json())['route']
        path = data['path']
        is_public = json.loads(data.get(
            'is_public', "false"))

        try:
            fn_app = await fnclient.apps.show(app, loop=c.event_loop)
        except Exception as ex:
            return web.json_response(data={
                "error": {
                    "message": getattr(ex, "reason", str(ex)),
                }
            }, status=getattr(ex, "status", 500))

        try:
            await fn_app.routes.show(path, loop=c.event_loop)
            return web.json_response(data={
                "error": {
                    "message": (
                        "App {} route {} already exist"
                        .format(app, path)
                    )
                }
            }, status=409)
        except Exception as ex:
            if getattr(ex, "status", 500) != 404:
                return web.json_response(data={
                    "error": {
                        "message": getattr(ex, "reason", str(ex)),
                    }
                }, status=getattr(ex, "status", 500))

        new_fn_route = (await fn_app.routes.create(
            **data, loop=c.event_loop))

        stored_route = await app_model.Routes(
            app_name=new_fn_route.appname,
            project_id=project_id,
            path=new_fn_route.path,
            is_public=is_public).save()

        log.info("Creating new route in app {} "
                 "for project: {} with data {}"
                 .format(app, project_id, str(data)))
        api_url = "{}://{}".format(request.scheme, request.host)

        setattr(new_fn_route, "is_public", stored_route.public)
        view = app_view.AppRouteView(
            api_url, project_id, [new_fn_route]).view_one()

        return web.json_response(data={
            "route": view,
            "message": "App route successfully created"
        }, status=200)

    @requests.api_action(
        method='GET', route='{project_id}/apps/{app}/routes/{route}')
    async def get(self, request, **kwargs):
        """
        ---
        description: Pulling project-scoped app route
        tags:
        - Routes
        produces:
        - application/json
        responses:
            "200":
                description: Successful operation. Return "route" JSON
            "401":
                description: Not authorized.
            "404":
                description: App does not exist
            "404":
                description: App route does not exist
        """
        c = config.Config.config_instance()
        log, fnclient = c.logger, c.functions_client
        project_id = request.match_info.get('project_id')
        app = request.match_info.get('app')
        path = request.match_info.get('route')

        if not (await app_model.Apps.exists(app, project_id)):
            return web.json_response(data={
                "error": {
                    "message": "App {0} not found".format(app),
                }
            }, status=404)

        try:
            fn_app = await fnclient.apps.show(app, loop=c.event_loop)
            route = await fn_app.routes.show(
                "/{}".format(path), loop=c.event_loop)
        except Exception as ex:
            return web.json_response(data={
                "error": {
                    "message": getattr(ex, "reason", str(ex)),
                }
            }, status=getattr(ex, "status", 500))

        log.info("Requesting route {} in app {} for project: {}"
                 .format(path, app, project_id))

        api_url = "{}://{}".format(request.scheme, request.host)

        stored_route = (await app_model.Routes.find_by(
            app_name=app,
            project_id=project_id,
            path=route.path)).pop()

        setattr(route, "is_public", stored_route.public)

        return web.json_response(data={
            "route": app_view.AppRouteView(api_url,
                                           project_id,
                                           [route]).view_one(),
            "message": "App route successfully loaded"
        }, status=200)

    @requests.api_action(
        method='DELETE', route='{project_id}/apps/{app}/routes/{route}')
    async def delete(self, request, **kwargs):
        """
        ---
        description: Deleting project-scoped app route
        tags:
        - Routes
        produces:
        - application/json
        responses:
            "200":
                description: Successful operation. Return empty JSON
            "401":
                description: Not authorized.
            "404":
                description: App does not exist
            "404":
                description: App route does not exist
        """
        c = config.Config.config_instance()
        log, fnclient = c.logger, c.functions_client
        project_id = request.match_info.get('project_id')
        app = request.match_info.get('app')
        path = request.match_info.get('route')
        log.info("Deleting route {} in app {} for project: {}"
                 .format(path, app, project_id))

        if not (await app_model.Apps.exists(app, project_id)):
            return web.json_response(data={
                "error": {
                    "message": "App {0} not found".format(app),
                }
            }, status=404)

        try:
            fn_app = await fnclient.apps.show(app, loop=c.event_loop)
            await fn_app.routes.show("/{}".format(path), loop=c.event_loop)
            await fn_app.routes.delete("/{}".format(path), loop=c.event_loop)
            await app_model.Routes.delete(project_id=project_id, app_name=app)
        except Exception as ex:
            return web.json_response(data={
                "error": {
                    "message": getattr(ex, "reason", str(ex)),
                }
            }, status=getattr(ex, "status", 500))

        return web.json_response(data={
            "message": "Route successfully deleted",
        }, status=200)
