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
import uvloop

from laos.api.controllers import apps
from laos.api.controllers import routes
from laos.api.controllers import runnable
from laos.api.controllers import tasks

from laos.api.middleware import content_type
from laos.api.middleware import keystone

from laos.common.base import service
from laos.common import config
from laos.common import logger as log


class API(service.AbstractWebServer):

    def __init__(self, host: str='0.0.0.0',
                 port: int=10001,
                 loop: asyncio.AbstractEventLoop=asyncio.get_event_loop(),
                 logger=None,
                 debug=False):
        super(API, self).__init__(
            host=host,
            port=port,
            private_controllers={
                "v1": [
                    apps.AppV1Controller,
                    routes.AppRouteV1Controller,
                    tasks.TasksV1Controller,
                ],
                "private": [
                    runnable.RunnableV1Controller,
                ]
            },
            public_controllers={
                "public": [
                    runnable.PublicRunnableV1Controller,
                ],
            },
            private_middlewares=[
                keystone.auth_through_token,
                content_type.content_type_validator,
            ],
            public_middlewares=[
                content_type.content_type_validator,
            ],
            event_loop=loop,
            logger=logger,
            debug=debug,
        )


@click.command(name='laos-api')
@click.option('--host', default='0.0.0.0', help='API service bind host.')
@click.option('--port', default=10001, help='API service bind port.')
@click.option('--db-uri', default='mysql://root:root@localhost/functions',
              help='LaOS persistence storage URI.')
@click.option('--keystone-endpoint', default='http://localhost:5000/v3',
              help='OpenStack Identity service endpoint.')
@click.option('--functions-host', default='localhost',
              help='Functions API host')
@click.option('--functions-port', default=10501,
              help='Functions API port')
@click.option('--functions-api-version', default='v1',
              help='Functions API version')
@click.option('--functions-api-protocol', default='http',
              help='Functions API protocol')
@click.option('--log-level', default='INFO',
              help='Logging file')
@click.option('--log-file', default=None,
              help='Log file path')
@click.option('--debug', default=False, is_flag=True)
def server(host, port, db_uri,
           keystone_endpoint,
           functions_host,
           functions_port,
           functions_api_version,
           functions_api_protocol,
           log_level,
           log_file,
           debug,
           ):
    """
    Starts an Project Laos API service
    """
    logger = log.UnifiedLogger(
        log_to_console=True if not log_file else False,
        filename=None if not log_file else log_file,
        level=log_level).setup_logger(__package__)

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    loop = asyncio.get_event_loop()

    fnclient = config.FunctionsClient(
        functions_host,
        api_port=functions_port,
        api_protocol=functions_api_protocol,
        api_version=functions_api_version,
    )
    loop.run_until_complete(fnclient.ping(loop=loop))
    conn = config.Connection(db_uri, loop=loop)

    config.Config(
        auth_url=keystone_endpoint,
        functions_client=fnclient,
        logger=logger,
        connection=conn,
        event_loop=loop,
    )

    API(host=host, port=port, loop=loop,
        logger=logger, debug=debug).initialize()


if __name__ == "__main__":
    server()
