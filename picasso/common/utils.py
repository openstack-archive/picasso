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

from urllib import parse


def split_db_uri(db_uri):
    """
    Splits DB URI into consumable parts like:
        - username
        - password
        - hostname
        - port
        - protocol schema
        - path

    :param db_uri:
    :return:
    """
    parts = parse.urlparse(db_uri)
    return (parts.username, parts.password,
            parts.hostname, parts.port, parts.path[1:])


class Singleton(type):
    _instance = None

    def __call__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(
                Singleton, cls).__call__(*args, **kwargs)
        return cls._instance
