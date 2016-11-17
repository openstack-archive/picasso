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


class AppV1Controller(controllers.ServiceControllerBase):

    controller_name = "apps"
    version = "v1"

    @controllers.api_action(method='GET', route='{project_id}/apps')
    async def list(self, request, **kwargs):
        """
        ---
        description: Listing project-scoped apps
        tags:
        - Apps
        produces:
        - application/json
        responses:
            "200":
                description: successful operation. Return "apps" JSON
            "401":
                description: Not authorized.
        """
        c = config.Config.config_instance()
        log, fnclient = c.logger, c.functions_client
        project_id = request.match_info.get('project_id')
        log.info("Listing apps for project: {}".format(project_id))
        stored_apps = await app_model.Apps.find_by(project_id=project_id)
        final = []
        for app in stored_apps:
            fn_app = await fnclient.apps.show(app.name, loop=c.event_loop)
            final.append(app_view.AppView(app, fn_app).view())
        return web.json_response(
            data={
                self.controller_name: final,
                'message': "Successfully listed applications"
            },
            status=200
        )

    @controllers.api_action(method='POST', route='{project_id}/apps')
    async def create(self, request, **kwargs):
        """
        ---
        description: Creating project-scoped app
        tags:
        - Apps
        produces:
        - application/json
        parameters:
        - in: body
          name: app
          description: Created project-scoped app
          required: true
          schema:
            type: object
            properties:
              name:
                type: string
        responses:
            "200":
                description: successful operation. Return "app" JSON
            "401":
                description: Not authorized.
            "409":
                description: App exists
        """
        c = config.Config.config_instance()
        log, fnclient = c.logger, c.functions_client
        project_id = request.match_info.get('project_id')
        data = await request.json()
        log.info("Creating an app for project: {} with data {}"
                 .format(project_id, str(data)))
        app_name = "{}-{}".format(
            data["app"]["name"],
            project_id)[:30]

        if await app_model.Apps.exists(app_name, project_id):
            return web.json_response(data={
                "error": {
                    "message": "App {0} already exists".format(app_name)
                }
            }, status=409)

        fn_app = await fnclient.apps.create(app_name, loop=c.event_loop)
        stored_app = await app_model.Apps(
            name=app_name, project_id=project_id,
            description=data["app"].get(
                "description",
                "App for project {}".format(
                    project_id))).save()

        return web.json_response(
            data={
                "app": app_view.AppView(stored_app, fn_app).view(),
                "message": "App successfully created",
            }, status=200
        )

    @controllers.api_action(method='GET', route='{project_id}/apps/{app}')
    async def get(self, request, **kwargs):
        """
        ---
        description: Pulling project-scoped app
        tags:
        - Apps
        produces:
        - application/json
        responses:
            "200":
                description: successful operation. Return "app" JSON
            "401":
                description: Not authorized.
            "404":
                description: App not found
        """
        c = config.Config.config_instance()
        log, fnclient = c.logger, c.functions_client
        project_id = request.match_info.get('project_id')
        app = request.match_info.get('app')
        log.info("Requesting an app for project: {} with name {}"
                 .format(project_id, app))

        if not (await app_model.Apps.exists(app, project_id)):
            return web.json_response(data={
                "error": {
                    "message": "App {0} not found".format(app),
                }
            }, status=404)

        stored_app = (await app_model.Apps.find_by(
            project_id=project_id, name=app)).pop()
        fn_app = await fnclient.apps.show(app, loop=c.event_loop)
        return web.json_response(
            data={
                "app": app_view.AppView(stored_app, fn_app).view(),
                "message": "Successfully loaded app",
            },
            status=200
        )
    # TODO(denismakogon): disabled until iron-io/functions/pull/259
    #
    # @controllers.api_action(method='PUT', route='{project_id}/apps/{app}')
    # async def update(self, request, **kwargs):
    #     log = config.Config.config_instance().logger
    #     project_id = request.match_info.get('project_id')
    #     app = request.match_info.get('app')
    #     data = await request.json()
    #     log.info("Updating an app {} for project: {} with data {}"
    #              .format(app, project_id, str(data)))
    #     return web.json_response(
    #         data={
    #             "app": {}
    #         },
    #         status=200
    #     )

    @controllers.api_action(method='DELETE', route='{project_id}/apps/{app}')
    async def delete(self, request, **kwargs):
        """
        ---
        description: Deleting project-scoped app
        tags:
        - Apps
        produces:
        - application/json
        responses:
            "200":
                description: successful operation. Return empty JSON
            "401":
                description: Not authorized.
            "404":
                description: App does not exist
        """
        project_id = request.match_info.get('project_id')
        app = request.match_info.get('app')

        if not (await app_model.Apps.exists(app, project_id)):
            return web.json_response(data={
                "error": {
                    "message": "App {0} not found".format(app),
                }
            }, status=404)

        await app_model.Apps.delete(
            project_id=project_id, name=app)
        # TODO(denismakogon): enable DELETE to IronFunctions when once
        # https://github.com/iron-io/functions/issues/274 implemented
        # fn_app = await fnclient.apps.delete(app, loop=c.event_loop)
        return web.json_response(
            data={
                "message": "App successfully deleted",
            }, status=200)
