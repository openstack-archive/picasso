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

import click
import os
import uvloop


from aioservice.http import service

from picasso.api.controllers import apps
from picasso.api.controllers import routes
from picasso.api.controllers import runnable

from picasso.api.middleware import content_type
from picasso.api.middleware import keystone

from picasso.common import config
from picasso.common import logger as log

from urllib import parse


class API(service.HTTPService):

    def __init__(self, host: str='0.0.0.0',
                 port: int=10001,
                 loop: asyncio.AbstractEventLoop=asyncio.get_event_loop(),
                 logger=None,
                 debug=False):

        v1_service = service.VersionedService(
            [
                apps.AppV1Controller,
                routes.AppRouteV1Controller,
                runnable.RunnableV1Controller,
            ], middleware=[
                keystone.auth_through_token,
                content_type.content_type_validator
            ])

        public_runnable_service = service.VersionedService(
            [
                runnable.PublicRunnableV1Controller
            ], middleware=[
                content_type.content_type_validator,
            ]
        )

        super(API, self).__init__(
            host=host,
            port=port,
            event_loop=loop,
            logger=logger,
            debug=debug,
            subservice_definitions=[
                v1_service, public_runnable_service
            ]
        )


@click.command(name='picasso-api')
@click.option('--host',
              default=os.getenv("PICASSO_HOST", '0.0.0.0'),
              help='API service host.')
@click.option('--port', default=int(os.getenv("PICASSO_PORT", 10001)),
              help='API service port.')
@click.option('--db-uri',
              default=os.getenv(
                  "PICASSO_DB",
                  'mysql://root:root@localhost/functions'),
              help='Picasso persistence storage URI.')
@click.option('--keystone-endpoint',
              default=os.getenv("KEYSTONE_ENDPOINT",
                                'http://localhost:5000/v3'),
              help='OpenStack Identity service endpoint.')
@click.option('--functions-url',
              default=os.getenv(
                  "FUNCTIONS_URL", 'http://localhost:8080/v1'),
              help='Functions API host')
@click.option('--log-level',
              default=os.getenv("PICASSO_LOG_LEVEL", 'INFO'),
              help='Logging file')
@click.option('--log-file', default=os.getenv("PICASSO_LOG_FILE"),
              help='Log file path')
@click.option('--debug', default=False, is_flag=True)
def server(host, port, db_uri,
           keystone_endpoint,
           functions_url,
           log_level,
           log_file,
           debug,
           ):
    """
    Starts Picasso API service
    """
    logger = log.UnifiedLogger(
        log_to_console=True if not log_file else False,
        filename=None if not log_file else log_file,
        level=log_level).setup_logger(__package__)

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    loop = asyncio.get_event_loop()

    parts = parse.urlparse(functions_url)

    fnclient = config.FunctionsClient(
        parts.hostname,
        api_port=parts.port,
        api_protocol=parts.scheme,
        api_version=parts.path[1:]
    )
    loop.run_until_complete(fnclient.ping(loop=loop))
    connection_pool = config.Connection(db_uri, loop=loop)

    config.Config(
        auth_url=keystone_endpoint,
        functions_client=fnclient,
        logger=logger,
        connection=connection_pool,
        event_loop=loop,
    )

    API(
        host=host, port=port, loop=loop,
        logger=logger, debug=debug
    ).apply_swagger(
        swagger_url="/api",
        description="Picasso API service docs",
        api_version="v1.0.0",
        title="Picasso API",
    ).initialize()


if __name__ == "__main__":
    server()
