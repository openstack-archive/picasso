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

from aioservice.http import service
from oslo_utils import uuidutils

from ...api.controllers import apps
from ...api.controllers import routes
from ...api.controllers import runnable
from ...api.middleware import content_type

from ...common import config

from ..common import base
from ..common import client
from ..fakes import functions_api


class FunctionalTestsBase(base.PicassoTestsBase, testtools.TestCase):

    def setUp(self):
        self.testloop, logger = self.get_loop_and_logger("functional")

        v1_service = service.VersionedService(
            [
                apps.AppV1Controller,
                routes.AppRouteV1Controller,
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

        self.project_id = uuidutils.generate_uuid().replace("-", "")
        self.other_project_id = uuidutils.generate_uuid().replace("-", "")

        self.test_client = client.ProjectBoundTestClient(
            self.testapp, self.project_id)
        self.other_test_client = client.ProjectBoundTestClient(
            self.testapp, self.other_project_id)

        self.testloop.run_until_complete(self.test_client.start_server())
        super(FunctionalTestsBase, self).setUp()

    def tearDown(self):
        self.testloop.run_until_complete(self.test_client.close())
        self.testloop.run_until_complete(self.other_test_client.close())
        super(FunctionalTestsBase, self).tearDown()
