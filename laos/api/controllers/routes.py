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

from aiohttp import web

from laos.api.views import app as app_view

from laos.common.base import controllers
from laos.common import config

from laos.models import app as app_model


class AppRouteV1Controller(controllers.ServiceControllerBase):

    controller_name = "routes"
    version = "v1"

    @controllers.api_action(
        method='GET', route='{project_id}/apps/{app}/routes')
    async def list(self, request, **kwargs):
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

        fn_app_routes = (await (await fnclient.apps.show(
            app, loop=c.event_loop)).routes.list(loop=c.event_loop))

        log.info("Listing app {} routes for project: {}."
                 .format(app, project_id))
        return web.json_response(data={
            "routes": app_view.AppRouteView(fn_app_routes).view(),
            "message": "Successfully loaded app routes",
        }, status=200)

    @controllers.api_action(
        method='POST', route='{project_id}/apps/{app}/routes')
    async def create(self, request, **kwargs):
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

        new_fn_route = (await (await fnclient.apps.show(
            app, loop=c.event_loop)).routes.create(
            **data, loop=c.event_loop))

        log.info("Creating new route in app {} "
                 "for project: {} with data {}"
                 .format(app, project_id, str(data)))
        return web.json_response(data={
            "route": app_view.AppRouteView([new_fn_route]).view(),
            "message": "App route successfully created"
        }, status=200)

    @controllers.api_action(
        method='GET', route='{project_id}/apps/{app}/routes/{route}')
    async def get(self, request, **kwargs):
        c = config.Config.config_instance()
        log, fnclient = c.logger, c.functions_client
        project_id = request.match_info.get('project_id')
        app = request.match_info.get('app')
        path = request.match_info.get('route')

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
        return web.json_response(data={
            "route": app_view.AppRouteView([route]).view().pop(),
            "message": "App route successfully loaded"
        }, status=200)

    @controllers.api_action(
        method='DELETE', route='{project_id}/apps/{app}/routes/{route}')
    async def delete(self, request, **kwargs):
        c = config.Config.config_instance()
        log, fnclient = c.logger, c.functions_client
        project_id = request.match_info.get('project_id')
        app = request.match_info.get('app')
        path = request.match_info.get('route')
        log.info("Deleting route {} in app {} for project: {}"
                 .format(path, app, project_id))
        try:
            fn_app = await fnclient.apps.show(app, loop=c.event_loop)
            await fn_app.routes.show("/{}".format(path), loop=c.event_loop)
            await fn_app.routes.delete("/{}".format(path), loop=c.event_loop)
        except Exception as ex:
            return web.json_response(data={
                "error": {
                    "message": getattr(ex, "reason", str(ex)),
                }
            }, status=getattr(ex, "status", 500))

        return web.json_response(data={
            "message": "Route successfully deleted",
        }, status=200)
