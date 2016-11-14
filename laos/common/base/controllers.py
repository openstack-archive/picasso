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

import functools
import inspect

from aiohttp import web


class ServiceControllerBase(object):

    controller_name = 'abstract'
    version = ""

    def __get_handlers(self):
        # when this method gets executed by child classes
        # method list includes a method of parent class,
        # so this code ignores it because it doesn't belong to controllers
        methods = [getattr(self, _m)
                   for _m in dir(self) if inspect.ismethod(
                   getattr(self, _m)) and not _m.startswith("__")][1:]

        return [[method,
                 method.arg_method,
                 method.arg_route] for method in methods]

    def __init__(self, service: web.Application):
        for fn, http_method, route in self.__get_handlers():
            proxy_fn = '_'.join([fn.__name__, self.controller_name])
            setattr(self, proxy_fn, fn)
            service.router.add_route(http_method,
                                     "/{}/{}".format(self.version, route),
                                     getattr(self, proxy_fn),
                                     name=proxy_fn)


def api_action(**outter_kwargs):
    """
    Wrapps API controller action actions handler
    :param outter_kwargs: API instance action key-value args
    :return: _api_handler

    Example:

    class Controller(ControllerBase):

        @api_action(method='GET')
        async def index(self, request, **kwargs):
            return web.Response(
                text=str(request),
                reason="dumb API",
                status=201)

    """

    def _api_handler(func):

        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            return func(self, *args, *kwargs)

        for key, value in outter_kwargs.items():
            setattr(wrapper, 'arg_{}'.format(key), value)
        setattr(wrapper, 'is_module_function', True)
        return wrapper

    return _api_handler
