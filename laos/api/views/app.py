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


class AppView(object):

    def __init__(self, stored_app, fn_app):
        self.app = stored_app
        self.fn_app = fn_app

    def view(self):
        return {
            "id": self.app.id,
            "name": self.app.name,
            "config": self.fn_app.config,
            "description": self.app.description,
            "created_at": self.app.created_at,
            "updated_at": self.app.updated_at,
            "project_id": self.app.project_id,
        }


class AppRouteView(object):

    def __init__(self, api_url, project_id, app_name, fn_app_routes):
        self.routes = fn_app_routes
        self.api_url = api_url
        self.project_id = project_id
        self.app_name = app_name

    def view_one(self):
        return self.view().pop()

    def view(self):
        view = []
        for route in self.routes:
            if not route.is_public:
                path = ("{}/v1/r/{}/{}{}".format(
                    self.api_url, self.project_id,
                    self.app_name, route.path))
            else:
                path = ("{}/r/{}{}".format(
                    self.api_url, self.app_name, route.path))
            one = {
                "path": path,
                "type": route.type,
                "image": route.image,
                "is_public": route.is_public,
            }
            # temporary solution for
            # https://github.com/iron-io/functions/issues/382
            if hasattr(route, "memory"):
                one.update(memory=route.memory)
            if hasattr(route, "timeout"):
                one.update(timeout=route.timeout)
            if hasattr(route, "max_concurrency"):
                one.update(timeout=route.max_concurrency)
            view.append(one)
        return view
