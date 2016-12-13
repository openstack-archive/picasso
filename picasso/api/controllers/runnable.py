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

from aioservice.http import controller
from aioservice.http import requests

from ...common import config
from ...models import app as app_model


class RunnableMixin(object):

    async def run(self, request, **kwargs):
        c = config.Config.config_instance()
        log, fnclient = c.logger, c.functions_client
        app = request.match_info.get('app')
        path = "/{}".format(request.match_info.get('route'))

        try:
            data = await request.json()
        except Exception:
            # in may appear that no data supplied with POST to function
            data = {}

        try:
            fn_app = await fnclient.apps.show(
                app, loop=c.event_loop)
            route = await fn_app.routes.show(
                path, loop=c.event_loop)
            result = await fn_app.routes.execute(
                path, loop=c.event_loop, **data)
        except Exception as ex:
            log.error("Unable to execute route. "
                      "Reason:\n{}".format(str(ex)))
            return web.json_response(data={
                "error": {
                    "message": getattr(ex, "reason", str(ex)),
                }
            }, status=getattr(ex, "status", 500))

        def process_result(res):
            if route.type == "async":
                _data = {}
            else:
                _data = {
                    "result": res,
                    "message": ("App {} sync route {} "
                                "execution finished".format(app, path))
                }
            return _data

        return web.json_response(status=200, data=process_result(result))


class PublicRunnableV1Controller(controller.ServiceController,
                                 RunnableMixin):

    controller_name = "public_runnable"
    # IronFunction uses `r` as runnable instead API version
    version = "r"

    @requests.api_action(
        method='POST', route='{app}/{route}')
    async def run(self, request, **kwargs):
        """
        ---
        description: Running public app route
        tags:
        - Runnable
        produces:
        - application/json
        responses:
            "200":
                description: Successful operation
            "404":
                description: App not found
            "403":
                description: Unable to execute private route
        """
        log = config.Config.config_instance().logger
        app = request.match_info.get('app')
        path = "/{}".format(request.match_info.get('route'))
        routes = await app_model.Routes.find_by(
            app_name=app, path=path)

        if not routes:
            return web.json_response(data={
                "error": {
                    "message": "Route {0} not found".format(path),
                }
            }, status=404)
        route = routes.pop()

        if not route.public:
            log.info("Unable to execute private route '{}'".format(path))
            return web.json_response(data={
                "error": {
                    "message": "Unable to execute private "
                               "route {0}".format(path)
                }
            }, status=403)

        return await super(PublicRunnableV1Controller,
                           self).run(request, **kwargs)


class RunnableV1Controller(controller.ServiceController,
                           RunnableMixin):

    controller_name = "runnable"
    # IronFunction uses `r` as runnable instead API version
    version = "v1"

    @requests.api_action(
        method='POST', route='r/{project_id}/{app}/{route}')
    async def run(self, request, **kwargs):
        """
        ---
        description: Running private app route
        tags:
        - Runnable
        produces:
        - application/json
        responses:
            "401":
                description: Not authorized
            "200":
                description: Successful operation
            "404":
                description: App not found
            "404":
                description: App route not found
        """
        log = config.Config.config_instance().logger
        app = request.match_info.get('app')
        project_id = request.match_info.get('project_id')

        if not (await app_model.Apps.exists(app, project_id)):
            log.info("[{}] - App not found, "
                     "aborting".format(project_id))
            return web.json_response(data={
                "error": {
                    "message": "App {0} not found".format(app),
                }
            }, status=404)

        return await super(RunnableV1Controller,
                           self).run(request, **kwargs)
