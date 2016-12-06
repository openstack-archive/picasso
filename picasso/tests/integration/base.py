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
import os
from urllib import parse

import aiohttp
import testtools

from ...common import config
from ..common import base
from ..common import client


from service import picasso_api


class PicassoIntegrationTestsBase(base.PicassoTestsBase, testtools.TestCase):

    async def authenticate(self, os_user, os_pass, os_project, url):
        auth_request_data = {
            "auth": {
                "identity": {
                    "methods": ["password"],
                    "password": {
                        "user": {
                            "name": os_user,
                            "domain": {"id": "default"},
                            "password": os_pass
                        }
                    }
                },
                "scope": {
                    "project": {
                        "name": os_project,
                        "domain": {"id": "default"}
                    }
                }
            }
        }
        with aiohttp.ClientSession(loop=self.testloop) as session:
            response = await session.post(
                "{}/auth/tokens".format(url),
                data=json.dumps(auth_request_data),
                headers={
                    "Content-Type": "application/json"
                },
                timeout=20)
            response.raise_for_status()
            result = await response.json()
            return (response.headers["X-Subject-Token"],
                    result["token"]["project"]["id"])

    def setUp(self):

        self.testloop, logger = self.get_loop_and_logger("integration")

        (functions_url, db_uri,
         os_auth_url, os_user, os_pass, os_project) = (
            os.getenv("FUNCTIONS_API_URL", "http://localhost:8080/v1"),
            os.getenv("TEST_DB_URI"),
            os.getenv("OS_AUTH_URL"),
            os.getenv("OS_USERNAME"),
            os.getenv("OS_PASSWORD"),
            os.getenv("OS_PROJECT_NAME"),
        )

        if not all([db_uri, os_auth_url, os_user, os_pass, os_project]):
            raise self.skipTest("Not all test env variables were set.")

        parts = parse.urlparse(functions_url)

        fnclient = config.FunctionsClient(
            parts.hostname,
            api_port=parts.port,
            api_protocol=parts.scheme,
            api_version=parts.path[1:]
        )
        self.testloop.run_until_complete(fnclient.ping(loop=self.testloop))
        connection_pool = config.Connection(db_uri, loop=self.testloop)

        config.Config(
            auth_url=os_auth_url,
            functions_client=fnclient,
            logger=logger,
            connection=connection_pool,
            event_loop=self.testloop,
        )

        self.test_app = picasso_api.API(
            loop=self.testloop, logger=logger, debug=True)

        os_token, project_id = self.testloop.run_until_complete(
            self.authenticate(
                os_user, os_pass,
                os_project, os_auth_url))

        self.test_client = client.ProjectBoundTestClient(
            self.test_app.root, project_id, headers={
                "X-Auth-Token": os_token
            })
        self.testloop.run_until_complete(
            self.test_client.start_server())
        super(PicassoIntegrationTestsBase, self).setUp()

    def tearDown(self):
        self.testloop.run_until_complete(self.test_client.close())
        super(PicassoIntegrationTestsBase, self).tearDown()
