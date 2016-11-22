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
import os
import testtools
import uuid

from aioservice.http import service

from laos.api.controllers import apps
from laos.api.controllers import routes
from laos.api.controllers import runnable
from laos.api.controllers import tasks
from laos.api.middleware import content_type

from laos.common import config

from laos.tests.common import base
from laos.tests.common import client
from laos.tests.fakes import functions_api


class LaosFunctionalTestsBase(base.LaosTestsBase, testtools.TestCase):

    def setUp(self):
        self.testloop, logger = self.get_loop_and_logger("functional")

        v1_service = service.VersionedService(
            [
                apps.AppV1Controller,
                routes.AppRouteV1Controller,
                tasks.TasksV1Controller,
                runnable.RunnableV1Controller,
            ], middleware=[
                content_type.content_type_validator
            ]
        )
        public_runnable = service.VersionedService(
            [
                runnable.PublicRunnableV1Controller,
            ], middleware=[
                content_type.content_type_validator,
            ]
        )
        self.testapp = service.HTTPService(
            [v1_service, public_runnable],
            port=10001,
            event_loop=self.testloop,
            logger=logger,
            debug=True,
        ).root

        connection_pool = config.Connection(
            os.getenv("TEST_DB_URI"), loop=self.testloop)

        fnclient = functions_api.FunctionsAPIV1()

        self.test_config = config.Config(
            logger=logger,
            connection=connection_pool,
            event_loop=self.testloop,
            functions_client=fnclient,
        )

        self.project_id = str(uuid.uuid4()).replace("-", "")
        self.test_client = client.ProjectBoundLaosTestClient(
            self.testapp, self.project_id)

        self.route_data = {
            "type": "sync",
            "path": "/hello-sync-private",
            "image": "iron/hello",
            "is_public": "false"
        }

        self.testloop.run_until_complete(self.test_client.start_server())
        super(LaosFunctionalTestsBase, self).setUp()

    def tearDown(self):
        functions_api.APPS = {}
        functions_api.ROUTES = collections.defaultdict(list)
        # ^ temporary solution,
        # until https://github.com/iron-io/functions/issues/274 fixed
        self.testloop.run_until_complete(self.test_client.close())
        super(LaosFunctionalTestsBase, self).tearDown()
