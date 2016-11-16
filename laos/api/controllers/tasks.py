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

# from laos.models import app as app_model

from laos.common.base import controllers
# from laos.common import config


# TODO(denismakogon): disabled until
# https://github.com/iron-io/functions/issues/275
class TasksV1Controller(controllers.ServiceControllerBase):

    controller_name = "tasks"
    version = "v1"

    # TODO(denismakogon):
    # - define subapp to process requests to tasks API:
    #   * extract tasks V1 controller to subapp
    # - on each request check if route is public our private
    #   * reject with 401 if route is private
    #   * accept with 200 if route is public
    @controllers.api_action(
        method='GET', route='{project_id}/tasks')
    async def get(self, request, **kwargs):
        # c = config.Config.config_instance()
        # fnclient = c.functions_client
        # project_id = request.match_info.get('project_id')
        # stored_apps = await app_model.Apps.find_by(project_id=project_id)
        # final = []
        # for app in stored_apps:
        #     fn_app = await fnclient.apps.show(app.name, loop=c.event_loop)

        return web.json_response(data={
            "error": {
                "message": "Not supported"
            }
        }, status=405)

    @controllers.api_action(
        method='GET', route='{project_id}/tasks/{task}')
    async def show(self, request, **kwargs):
        # c = config.Config.config_instance()
        # fnclient = c.functions_client
        # project_id = request.match_info.get('project_id')
        # stored_apps = await app_model.Apps.find_by(project_id=project_id)
        # final = []
        # for app in stored_apps:
        #     fn_app = await fnclient.apps.show(app.name, loop=c.event_loop)

        return web.json_response(data={
            "error": {
                "message": "Not supported"
            }
        }, status=405)
