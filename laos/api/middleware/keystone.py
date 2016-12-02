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

from keystoneauth1 import identity
from keystoneauth1 import session
from keystoneclient import client

from aiohttp import web

from ...common import config


async def auth_through_token(app: web.Application, handler):
    async def middleware_handler(request: web.Request):
        headers = request.headers
        x_auth_token = headers.get("X-Auth-Token")
        project_id = request.match_info.get('project_id')
        c = config.Config.config_instance()
        try:
            auth = identity.Token(c.auth_url,
                                  token=x_auth_token,
                                  project_id=project_id)
            sess = session.Session(auth=auth)
            ks = client.Client(session=sess,
                               project_id=project_id)
            ks.authenticate(token=x_auth_token)
        except Exception as ex:
            return web.json_response(status=401, data={
                "error": {
                    "message": ("Not authorized. Reason: {}"
                                .format(str(ex)))
                }
            })
        return await handler(request)
    return middleware_handler
