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

import json as jsonlib


class AppRoutesTestSuite(object):

    def list_routes_from_unknown_app(self):
        json, status = self.testloop.run_until_complete(
            self.test_client.routes.list("uknown_app")
        )
        self.assertEqual(status, 404)
        self.assertIn("error", json)
        self.assertIn("not found", json["error"]["message"])

    def list_routes_from_existing_app(self):
        create_json, _ = self.testloop.run_until_complete(
            self.test_client.apps.create("testapp"))
        json, status = self.testloop.run_until_complete(
            self.test_client.routes.list(create_json["app"]["name"])
        )
        self.testloop.run_until_complete(
            self.test_client.apps.delete(create_json["app"]["name"]))
        self.assertEqual(status, 200)
        self.assertIn("routes", json)
        self.assertIn("message", json)

    def show_unknown_route_from_existing_app(self):
        path = "/unknown_path"
        create_json, _ = self.testloop.run_until_complete(
            self.test_client.apps.create("testapp"))
        json, status = self.testloop.run_until_complete(
            self.test_client.routes.show(
                create_json["app"]["name"], path)
        )
        self.testloop.run_until_complete(
            self.test_client.apps.delete(create_json["app"]["name"]))

        self.assertEqual(404, status)
        self.assertIn("error", json)
        self.assertIn("not found", json["error"]["message"])

    def delete_unknown_route_from_existing_app(self):
        create_json, _ = self.testloop.run_until_complete(
            self.test_client.apps.create("testapp"))
        json, status = self.testloop.run_until_complete(
            self.test_client.routes.delete(
                create_json["app"]["name"], "/unknown_path")
        )
        self.testloop.run_until_complete(
            self.test_client.apps.delete(create_json["app"]["name"]))

        self.assertEqual(404, status)
        self.assertIn("error", json)
        self.assertIn("not found", json["error"]["message"])

    def create_and_delete_route(self):
        app, _ = self.testloop.run_until_complete(
            self.test_client.apps.create("testapp"))
        route, create_status = self.testloop.run_until_complete(
            self.test_client.routes.create(
                app["app"]["name"], **self.route_data)
        )
        route_deleted, delete_status = self.testloop.run_until_complete(
            self.test_client.routes.delete(
                app["app"]["name"], self.route_data["path"])
        )
        self.testloop.run_until_complete(
            self.test_client.apps.delete(app["app"]["name"]))
        after_post = route["route"]
        for k in self.route_data:
            if k == "path":
                self.assertIn(self.route_data["path"], after_post[k])
                continue
            if k == "is_public":
                is_public = jsonlib.loads(self.route_data[k])
                self.assertEqual(is_public, after_post[k])
                continue
            self.assertEqual(self.route_data[k], after_post[k])
        self.assertEqual(200, delete_status)
        self.assertEqual(200, create_status)
        self.assertIn("message", route_deleted)

    def double_create_route(self):
        app, _ = self.testloop.run_until_complete(
            self.test_client.apps.create("testapp"))
        self.testloop.run_until_complete(
            self.test_client.routes.create(
                app["app"]["name"], **self.route_data)
        )

        json, double_create_status = self.testloop.run_until_complete(
            self.test_client.routes.create(
                app["app"]["name"], **self.route_data)
        )
        self.testloop.run_until_complete(
            self.test_client.routes.delete(
                app["app"]["name"], self.route_data["path"])
        )
        self.testloop.run_until_complete(
            self.test_client.apps.delete(app["app"]["name"]))

        self.assertEqual(409, double_create_status)
        self.assertIn("error", json)
        self.assertIn("message", json["error"])
        self.assertIn("already exist", json["error"]["message"])
