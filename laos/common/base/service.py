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

import aiohttp_swagger

from aiohttp import web

from laos.common import logger as log


class AbstractWebServer(object):

    def __init__(self, host: str='127.0.0.1',
                 port: int= '10001',
                 private_controllers: dict=None,
                 private_middlewares: list=None,
                 public_middlewares: list=None,
                 public_controllers: dict=None,
                 event_loop: asyncio.AbstractEventLoop=None,
                 logger=log.UnifiedLogger(
                     log_to_console=True,
                     level="INFO").setup_logger(__name__),
                 debug=False):
        """
        HTTP server abstraction class
        :param host: Bind host
        :param port: Bind port
        :param private_controllers: private API controllers mapping
        :param private_middlewares: list of private API middleware
        :param public_middlewares:
                list of public API middleware
        :param public_controllers:
                public API controllers mapping
        :param event_loop: asyncio eventloop
        :param logger: logging.Logger
        """
        self.host = host
        self.port = port
        self.event_loop = event_loop
        self.logger = logger

        self.root_service = web.Application(
            logger=self.logger,
            loop=self.event_loop,
            debug=debug
        )

        self.register_subapps(private_controllers, private_middlewares)
        self.register_subapps(public_controllers, public_middlewares)

    def _apply_routers(self, service, controllers):
        for controller in controllers:
            controller(service)
        return service

    def register_subapps(self, controllers_mapping: dict, middlewares: list):
        if controllers_mapping:
            for sub_route, controllers in controllers_mapping.items():
                service = self._apply_routers(
                    web.Application(
                        logger=self.logger,
                        loop=self.event_loop,
                        middlewares=middlewares
                        if middlewares else []),
                    controllers)
                self.root_service.router.add_subapp(
                    "/{}/".format(sub_route), service)

    def initialize(self):
        aiohttp_swagger.setup_swagger(
            self.root_service, swagger_url="/api")
        web.run_app(self.root_service, host=self.host, port=self.port,
                    shutdown_timeout=10, access_log=self.logger)
