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

from ..common import persistence


class Apps(persistence.BaseDatabaseModel):

    table_name = "apps"
    columns = (
        "id",
        "project_id",
        "description",
        "created_at",
        "updated_at",
        "name"
    )


class Routes(persistence.BaseDatabaseModel):

    table_name = "routes"
    columns = (
        "project_id",
        "path",
        "is_public",
        "app_name",
        "created_at",
        "updated_at",
    )

    @property
    def public(self):
        return True if self.is_public else False
