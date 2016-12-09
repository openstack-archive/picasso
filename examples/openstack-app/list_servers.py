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

import json
import os
import sys

from keystoneauth1 import identity
from keystoneauth1 import session
from keystoneclient import client as keystone

from novaclient import client as nova


num_servers = 0

if not os.isatty(sys.stdin.fileno()):
    obj = json.loads(sys.stdin.read())
    auth_url = obj.get("OS_AUTH_URL")
    x_auth_token = obj.get("OS_TOKEN")
    project_id = obj.get("OS_PROJECT_ID")
    auth = identity.Token(auth_url,
                          token=x_auth_token,
                          project_id=project_id)
    sess = session.Session(auth=auth)
    ks = keystone.Client(session=sess,
                         project_id=project_id)
    ks.authenticate(token=x_auth_token)

    nc = nova.Client('2', session=sess)
    num_servers = len(nc.servers.list())

print("You have", num_servers, "servers.")
