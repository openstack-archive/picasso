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

from laos.common.base import controllers
from laos.common import config


class RunnableMixin(object):

    async def run(self, request, **kwargs):
        c = config.Config.config_instance()
        fnclient = c.functions_client
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
            return web.json_response(data={
                "error": {
                    "message": getattr(ex, "reason", str(ex)),
                }
            }, status=getattr(ex, "status", 500))

        def process_result(res):
            if route.type == "async":
                _data = {
                    "task_id": res["call_id"],
                    "message": ("App {} async route {} "
                                "execution started".format(app, path))
                }
            else:
                _data = {
                    "result": res,
                    "message": ("App {} sync route {} "
                                "execution finished".format(app, path))
                }
            return _data

        return web.json_response(status=200, data=process_result(result))


class PublicRunnableV1Controller(controllers.ServiceControllerBase,
                                 RunnableMixin):

    controller_name = "public_runnable"
    # IronFunction uses `r` as runnable instead API version
    version = "r"

    @controllers.api_action(
        method='POST', route='{app}/{route}')
    async def run(self, request, **kwargs):
        return await super(PublicRunnableV1Controller,
                           self).run(request, **kwargs)


class RunnableV1Controller(controllers.ServiceControllerBase,
                           RunnableMixin):

    controller_name = "runnable"
    # IronFunction uses `r` as runnable instead API version
    version = "r"

    @controllers.api_action(
        method='POST', route='{project_id}/{app}/{route}')
    async def run(self, request, **kwargs):
        return await super(RunnableV1Controller,
                           self).run(request, **kwargs)
