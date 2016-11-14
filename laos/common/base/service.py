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

import asyncio
import os
import typing

from aiohttp import web
from laos.common.base import controllers as c
from laos.common import logger as log


class AbstractWebServer(object):

    def __init__(self, host: str='127.0.0.1',
                 port: int= '10001',
                 controllers: typing.List[c.ServiceControllerBase]=None,
                 middlewares: list=None,
                 event_loop: asyncio.AbstractEventLoop=None,
                 logger=log.UnifiedLogger(
                     log_to_console=True,
                     level="INFO").setup_logger(__name__)):
        """
        HTTP server abstraction class
        :param host:
        :param port:
        :param controllers:
        :param middlewares:
        :param event_loop:
        :param logger:
        """
        self.host = host
        self.port = port
        self.controllers = controllers
        self.event_loop = event_loop
        self.service = web.Application(
            loop=self.event_loop,
            debug=os.environ.get('PYTHONASYNCIODEBUG', 0),
            middlewares=middlewares if middlewares else [])
        self.service_handler = None
        self.server = None
        self.logger = logger

    def _apply_routers(self):
        if self.controllers:
            for controller in self.controllers:
                controller(self.service)

    def shutdown(self):
        self.server.close()
        self.event_loop.run_until_complete(self.server.wait_closed())
        self.event_loop.run_until_complete(
            self.service_handler.finish_connections(1.0))
        self.event_loop.run_until_complete(self.service.cleanup())

    def initialize(self):
        self._apply_routers()
        try:
            web.run_app(self.service, host=self.host, port=self.port,
                        shutdown_timeout=10, access_log=self.logger)
        except KeyboardInterrupt:
            self.shutdown()
