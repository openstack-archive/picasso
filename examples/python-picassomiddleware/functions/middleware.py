# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json

from swift.common.http import is_success
from swift.common.swob import Request
from swift.common.utils import split_path, get_logger

from eventlet import Timeout
import six
if six.PY3:
    from eventlet.green.urllib import request as urllib2
else:
    from eventlet.green import urllib2


class FunctionsWebhookMiddleware(object):

    def __init__(self, app, conf):
        self.app = app
        self.logger = get_logger(conf, log_route='serverless_functions')

    def __call__(self, env, start_response):
        req = Request(env)
        resp = req.get_response(self.app)
        self.logger.info("Serverless: available headers: {}".format(str(dict(req.headers))))
        try:
            if "X-Function-URL" in req.headers:
                version, account, container, obj = split_path(req.path_info, 4, 4, True)
                self.logger.info("Serverless: version {}, account {}, container {}, object {}"
                                 .format(version, account, container, obj))
                if obj and is_success(resp.status_int) and req.method == 'PUT':
                    webhook = req.headers.get("X-Function-URL")
                    data = json.dumps({
                        "x-auth-token": req.headers.get("X-Auth-Token"),
                        "version": version,
                        "account": account,
                        "container": container,
                        "object": obj,
                        "project_id": req.headers.get("X-Project-Id"),
                    })
                    self.logger.info("Serverless: data to send to a function {}"
                                     .format(str(data)))
                    data_as_bytes = data.encode('utf-8')
                    webhook_req = urllib2.Request(webhook, data=data_as_bytes)
                    webhook_req.add_header('Content-Type',
                                           'application/json')
                    webhook_req.add_header(
                        'Content-Length', len(data_as_bytes))
                    self.logger.info("Serverless: data to send as bytes {}"
                                     .format(data_as_bytes))
                    with Timeout(60):
                        try:
                            result = urllib2.urlopen(webhook_req).read()
                            self.logger.info(
                                "Serverless: function worked fine. Result {}"
                                .format(str(result)))
                        except (Exception, Timeout) as ex:
                            self.logger.error(
                                'Serverless: failed POST to webhook {}, '
                                'error {}'.format(webhook, str(ex)))
            else:
                self.logger.info("Serverless: skipping functions middleware "
                                 "due to absence of function URL")
        except ValueError:
            # not an object request
            pass

        return self.app(env, start_response)


def filter_factory(global_conf, **local_conf):
    conf = global_conf.copy()
    conf.update(local_conf)

    def webhook_filter(app):
        return FunctionsWebhookMiddleware(app, conf)
    return webhook_filter
