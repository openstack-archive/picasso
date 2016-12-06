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


import aiomysql
import asyncio

from . import utils

from functionsclient.v1 import client


class Config(object, metaclass=utils.Singleton):

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
        self.config = self

    @classmethod
    def config_instance(cls):
        return cls._instance.config


class Connection(object, metaclass=utils.Singleton):

    def __init__(self, db_uri, loop=None):
        self.uri = db_uri
        self.loop = loop
        self.pool = loop.run_until_complete(self.get_pool())
        self.loop = loop

    def get_pool(self):
        username, password, host, port, db_name = utils.split_db_uri(self.uri)
        return aiomysql.create_pool(host=host, port=port if port else 3306,
                                    user=username, password=password,
                                    db=db_name, loop=self.loop)

    @classmethod
    def from_class(cls):
        return cls._instance.pool


class FunctionsClient(client.FunctionsAPIV1, metaclass=utils.Singleton):

    def __init__(self, api_host: str,
                 api_port: int=8080,
                 api_protocol: str="http",
                 api_version: str="v1"):
        # TODO(denismakogon): enable API version discovery
        super(FunctionsClient, self).__init__(api_host, api_port, api_protocol)
        self.client = self

    async def ping(self,
                   loop: asyncio.AbstractEventLoop=asyncio.get_event_loop()):
        await self.apps.list(loop=loop)

    @classmethod
    def from_class(cls):
        return cls._instance.client
