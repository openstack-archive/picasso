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

import os
import testtools

from laos.common import config
from laos.service import laos_api

from laos.tests.common import base
from laos.tests.common import client


class LaosIntegrationTestsBase(base.LaosTestsBase, testtools.TestCase):

    def setUp(self):

        self.testloop, logger = self.get_loop_and_logger("integration")

        (functions_host, functions_port,
         functions_api_protocol,
         functions_api_version, db_uri,
         keystone_endpoint, project_id, os_token) = (
            os.getenv("FUNCTIONS_HOST"), os.getenv("FUNCTIONS_PORT", 8080),
            os.getenv("FUNCTIONS_API_PROTO", "http"),
            os.getenv("FUNCTIONS_API_VERSION", "v1"), os.getenv("TEST_DB_URI"),
            os.getenv("OS_AUTH_URL"), os.getenv("OS_PROJECT_ID"),
            os.getenv("OS_TOKEN"),
        )

        fnclient = config.FunctionsClient(
            functions_host,
            api_port=functions_port,
            api_protocol=functions_api_protocol,
            api_version=functions_api_version,
        )
        self.testloop.run_until_complete(fnclient.ping(loop=self.testloop))
        connection_pool = config.Connection(db_uri, loop=self.testloop)

        config.Config(
            auth_url=keystone_endpoint,
            functions_client=fnclient,
            logger=logger,
            connection=connection_pool,
            event_loop=self.testloop,
        )

        self.test_app = laos_api.API(
            loop=self.testloop, logger=logger, debug=True)

        self.test_client = client.ProjectBoundLaosTestClient(
            self.test_app.root_service, project_id, headers={
                "X-Auth-Token": os_token
            })
        self.testloop.run_until_complete(
            self.test_client.start_server())
        super(LaosIntegrationTestsBase, self).setUp()

    def tearDown(self):
        self.testloop.run_until_complete(self.test_client.close())
        super(LaosIntegrationTestsBase, self).tearDown()
