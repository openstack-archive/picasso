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

from ..common import apps as apps_suite
from ..integration import base


class TestIntegrationApps(base.PicassoIntegrationTestsBase,
                          apps_suite.AppsTestSuite):

    def test_list_apps(self):
        super(TestIntegrationApps, self).list_apps()

    def test_get_unknown(self):
        super(TestIntegrationApps, self).get_unknown()

    def test_create_and_delete(self):
        super(TestIntegrationApps, self).create_and_delete()

    def test_attempt_to_double_create(self):
        super(TestIntegrationApps, self).attempt_to_double_create()

    def test_attempt_delete_unknonw(self):
        super(TestIntegrationApps, self).attempt_delete_unknonw()

    def test_delete_with_routes(self):
        super(TestIntegrationApps, self).delete_with_routes()

    def test_update_app(self):
        super(TestIntegrationApps, self).update_app()
