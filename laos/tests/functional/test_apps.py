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

from laos.tests.functional import base


class TestApps(base.LaosFunctionalTestsBase):

    def test_list_apps(self):
        json, http_status = self.testloop.run_until_complete(
            self.test_client.apps.list())
        self.assertIn("message", json)
        self.assertIn("apps", json)
        self.assertEqual(200, http_status)

    def test_get_unknown(self):
        json, http_status = self.testloop.run_until_complete(
            self.test_client.apps.show("unknown"))
        self.assertEqual(404, http_status)
        self.assertIn("error", json)

    def test_create_and_delete(self):
        create_json, create_status = self.testloop.run_until_complete(
            self.test_client.apps.create("testapp"))
        delete_json, delete_status = self.testloop.run_until_complete(
            self.test_client.apps.delete(create_json["app"]["name"]))

        self.assertIn("message", create_json)
        self.assertIn("app", create_json)
        self.assertEqual(200, create_status)

        self.assertIn("message", delete_json)
        self.assertEqual(200, delete_status)

    def test_attempt_to_double_create(self):
        app = "testapp"
        create_json, _ = self.testloop.run_until_complete(
            self.test_client.apps.create(app))
        err, status = self.testloop.run_until_complete(
            self.test_client.apps.create(app))
        self.testloop.run_until_complete(
            self.test_client.apps.delete(create_json["app"]["name"]))
        self.assertEqual(409, status)
        self.assertIn("error", err)
        self.assertIn("message", err["error"])

    def test_attempt_delete_unknonw(self):
        json, http_status = self.testloop.run_until_complete(
            self.test_client.apps.delete("unknown"))
        self.assertEqual(404, http_status)
        self.assertIn("error", json)
