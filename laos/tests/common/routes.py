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

import contextlib
import json as jsonlib


@contextlib.contextmanager
def setup_execute(self, app_name):
    app, _ = self.testloop.run_until_complete(
        self.test_client.apps.create(app_name)
    )
    new_app_name = app["app"]["name"]
    route, _ = self.testloop.run_until_complete(
        self.test_client.routes.create(
            new_app_name, **self.route_data)
    )
    self.testloop.run_until_complete(
        self.test_client.routes.update(
            new_app_name, self.route_data["path"], **{
                "type": "sync"
            }
        )
    )
    try:
        yield new_app_name
    except Exception as ex:
        print(ex)
    finally:
        self.testloop.run_until_complete(
            self.test_client.routes.delete(
                new_app_name, self.route_data["path"])
        )
        self.testloop.run_until_complete(
            self.test_client.apps.delete(new_app_name))


class AppRoutesTestSuite(object):

    def list_routes_from_unknown_app(self):
        json, status = self.testloop.run_until_complete(
            self.test_client.routes.list("uknown_app")
        )
        self.assertEqual(status, 404)
        self.assertIn("error", json)
        self.assertIn("not found", json["error"]["message"])

    def list_routes_from_existing_app(self):
        app = "list_routes_from_existing_app"
        create_json, _ = self.testloop.run_until_complete(
            self.test_client.apps.create(app))
        json, status = self.testloop.run_until_complete(
            self.test_client.routes.list(create_json["app"]["name"])
        )
        self.testloop.run_until_complete(
            self.test_client.apps.delete(create_json["app"]["name"]))
        self.assertEqual(status, 200)
        self.assertIn("routes", json)
        self.assertIn("message", json)

    def show_unknown_route_from_existing_app(self):
        app = "show_unknown_route_from_existing_app"
        path = "/unknown_path"
        create_json, _ = self.testloop.run_until_complete(
            self.test_client.apps.create(app))
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
        app = "delete_unknown_route_from_existing_app"
        create_json, _ = self.testloop.run_until_complete(
            self.test_client.apps.create(app))
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
        app_name = "create_and_delete_route"
        created, _ = self.testloop.run_until_complete(
            self.test_client.apps.create(app_name))
        new_app_name = created["app"]["name"]
        route, create_status = self.testloop.run_until_complete(
            self.test_client.routes.create(
                new_app_name, **self.route_data)
        )
        route_deleted, delete_status = self.testloop.run_until_complete(
            self.test_client.routes.delete(
                new_app_name, self.route_data["path"])
        )
        self.testloop.run_until_complete(
            self.test_client.apps.delete(new_app_name))

        print(route)

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
        app = "double_create_route"
        created_app, _ = self.testloop.run_until_complete(
            self.test_client.apps.create(app))
        new_app_name = created_app["app"]["name"]

        self.testloop.run_until_complete(
            self.test_client.routes.create(
                new_app_name, **self.route_data)
        )

        json, double_create_status = self.testloop.run_until_complete(
            self.test_client.routes.create(
                new_app_name, **self.route_data)
        )
        self.testloop.run_until_complete(
            self.test_client.routes.delete(
                new_app_name, self.route_data["path"])
        )
        self.testloop.run_until_complete(
            self.test_client.apps.delete(new_app_name))

        self.assertEqual(409, double_create_status)
        self.assertIn("error", json)
        self.assertIn("message", json["error"])
        self.assertIn("already exist", json["error"]["message"])

    def update_route(self):
        app = "update_route"
        created, _ = self.testloop.run_until_complete(
            self.test_client.apps.create(app)
        )
        new_app_name = created["app"]["name"]
        route, _ = self.testloop.run_until_complete(
            self.test_client.routes.create(
                new_app_name, **self.route_data)
        )
        print(route)
        updated, update_status = self.testloop.run_until_complete(
            self.test_client.routes.update(
                new_app_name, self.route_data["path"], **{
                    "type": "sync"
                }
            )
        )
        print(updated)
        self.testloop.run_until_complete(
            self.test_client.routes.delete(
                new_app_name, self.route_data["path"])
        )
        self.testloop.run_until_complete(
            self.test_client.apps.delete(new_app_name))

        self.assertEqual(200, update_status)
        self.assertNotIn(route["route"]["type"], updated["route"]["type"])

    def execute_private(self):
        with setup_execute(self, "execute_private") as app_name:
            result, status = self.testloop.run_until_complete(
                self.test_client.routes.execute_private(
                    app_name, self.route_data["path"]
                )
            )
            self.assertIsNotNone(result)
            self.assertEqual(200, status)

    def execute_public(self):
        with setup_execute(self, "execute_public") as app_name:
            result, status = self.testloop.run_until_complete(
                self.test_client.routes.execute_public(
                    app_name, self.route_data["path"]
                )
            )
            self.assertIsNotNone(result)
            self.assertEqual(200, status)
