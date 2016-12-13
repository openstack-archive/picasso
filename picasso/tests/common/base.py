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
import datetime
import uvloop

from ...common import logger as log


class PicassoTestsBase(object):

    def get_loop_and_logger(self, test_type):
        self.route_data = {
            "type": "async",
            "path": "/hello-sync-private",
            "image": "iron/hello",
            "is_public": "false"
        }
        try:
            testloop = asyncio.get_event_loop()
        except Exception:
            asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
            testloop = asyncio.get_event_loop()

        logger = log.UnifiedLogger(
            log_to_console=False,
            filename=("./picasso-{}-tests-run-{}.log"
                      .format(test_type, datetime.datetime.now())),
            level="DEBUG").setup_logger(__package__)
        return testloop, logger
