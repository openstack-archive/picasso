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

import datetime
import logging
import sys

from laos.common import utils


def common_logger_setup(
        level=logging.DEBUG,
        filename='/tmp/laos-api.log',
        log_formatter='[%(asctime)s] - '
                      '%(name)s - '
                      '%(levelname)s - '
                      '%(module)s.py:%(lineno)d - '
                      '%(funcName)s - '
                      '%(message)s',
        datetime_formatter='%Y-%m-%d %H:%M:%S',
        log_to_console=False):
    if log_to_console:
        log_handler = logging.StreamHandler(sys.stdout)
    else:
        log_handler = logging.FileHandler(filename)
    log_format = logging.Formatter(log_formatter, datetime_formatter)
    log_handler.setFormatter(log_format)
    return log_handler, level


def setup_logging(name,
                  filename='/tmp/laos-api-{}.log'.format(
                      datetime.datetime.now()),
                  level=logging.DEBUG,
                  log_to_console=False,
                  formatter=None):
    log_file_handler, log_level = common_logger_setup(
        filename=filename,
        level=level,
        log_to_console=log_to_console,
        log_formatter=formatter)
    logger = logging.getLogger(name)
    logger.addHandler(log_file_handler)
    logger.setLevel(log_level)
    return logger


class Singleton(type):
    _instance = None

    def __call__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instance


class UnifiedLogger(object, metaclass=utils.Singleton):

    def __init__(self,
                 filename='/tmp/laos-api-{}.log'.format(
                     datetime.datetime.now()),
                 level=logging.DEBUG, log_to_console=False):
        self.filename = filename
        self.level = level
        if 'DEBUG' not in level:
            self.log_formatter = (
                '[%(asctime)s] - '
                '%(name)s - '
                '%(module)s.py:%(lineno)d - '
                '%(message)s'
            )
        else:
            self. log_formatter = (
                '[%(asctime)s] - '
                '%(name)s - '
                '%(levelname)s - '
                '%(module)s.py:%(lineno)d - '
                '%(funcName)s - '
                '%(message)s')
        self.log_to_console = log_to_console
        self.logger = self

    def setup_logger(self, name):
        return setup_logging(name, filename=self.filename,
                             level=self.level,
                             log_to_console=self.log_to_console,
                             formatter=self.log_formatter)
