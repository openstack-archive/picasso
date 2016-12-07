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


class AppsTestSuite(object):

    def list_apps(self):
        json, http_status = self.testloop.run_until_complete(
            self.test_client.apps.list())
        self.assertIn("message", json)
        self.assertIn("apps", json)
        self.assertEqual(200, http_status)

    def get_unknown(self):
        json, http_status = self.testloop.run_until_complete(
            self.test_client.apps.show("unknown"))
        self.assertEqual(404, http_status)
        self.assertIn("error", json)

    def create_and_delete(self):
        app = "create_and_delete"
        create_json, create_status = self.testloop.run_until_complete(
            self.test_client.apps.create(app))
        delete_json, delete_status = self.testloop.run_until_complete(
            self.test_client.apps.delete(create_json["app"]["name"]))

        self.assertIn("message", create_json)
        self.assertIn("app", create_json)
        self.assertEqual(200, create_status)

        self.assertIn("message", delete_json)
        self.assertEqual(200, delete_status)

    def attempt_to_double_create(self):
        app = "attempt_to_double_create"
        create_json, _ = self.testloop.run_until_complete(
            self.test_client.apps.create(app))
        err, status = self.testloop.run_until_complete(
            self.test_client.apps.create(app))
        self.testloop.run_until_complete(
            self.test_client.apps.delete(create_json["app"]["name"]))
        self.assertEqual(409, status)
        self.assertIn("error", err)
        self.assertIn("message", err["error"])

    def attempt_delete_unknonw(self):
        json, http_status = self.testloop.run_until_complete(
            self.test_client.apps.delete("unknown"))
        self.assertEqual(404, http_status)
        self.assertIn("error", json)

    def delete_with_routes(self):
        app_name = "delete_with_routes"
        app, _ = self.testloop.run_until_complete(
            self.test_client.apps.create(app_name))
        self.testloop.run_until_complete(
            self.test_client.routes.create(
                app["app"]["name"], **self.route_data)
        )
        attempt, status = self.testloop.run_until_complete(
            self.test_client.apps.delete(app["app"]["name"])
        )
        self.testloop.run_until_complete(
            self.test_client.routes.delete(
                app["app"]["name"], self.route_data["path"])
        )
        _, status_2 = self.testloop.run_until_complete(
            self.test_client.apps.delete(app["app"]["name"])
        )
        self.assertEqual(403, status)
        self.assertIn("error", attempt)
        self.assertIn("message", attempt["error"])
        self.assertIn("with routes", attempt["error"]["message"])
        self.assertEqual(200, status_2)

    def update_app(self):
        app_name = "update_app"
        app, _ = self.testloop.run_until_complete(
            self.test_client.apps.create(app_name))
        _, update_status = self.testloop.run_until_complete(
            self.test_client.apps.update(
                app["app"]["name"], config={}
            )
        )
        self.testloop.run_until_complete(
            self.test_client.apps.delete(app["app"]["name"]))
        self.assertEqual(200, update_status)
