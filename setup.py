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

import os
import setuptools


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setuptools.setup(
    name='laos',
    version='0.0.1',
    description='Project LaOS (Lambdas-on-OpenStack',
    long_description=read('README.md'),
    url='laos.readthedocs.org',
    author='Denis Makogon',
    author_email='denis@iron.io',
    packages=setuptools.find_packages(),
    install_requires=[
        "uvloop",
        "aiohttp",
        "aiomysql",
        "alembic>=0.8.4",
        "click",
        "keystoneauth1>=2.14.0",
        "python-keystoneclient==3.6.0",
        "aiohttp-swagger",
    ],
    license='License :: OSI Approved :: Apache Software License',
    classifiers=[
        'License :: OSI Approved :: Apache Software License',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Developers',
        'Environment :: No Input/Output (Daemon)',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Software Development :: '
        'Libraries :: Python Modules',
        'Topic :: System :: Distributed Computing',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Operating System :: Unix',
        'Operating System :: MacOS',
    ],
    keywords=['functions', 'lambdas', 'python API'],
    platforms=['Linux', 'Mac OS-X', 'Unix'],
    tests_require=[
        'flake8==2.5.0',
        'hacking<0.11,>=0.10.0',
        'coverage>=4.0',
        'sphinx!=1.3b1,<1.4,>=1.2.1',
        'testrepository>=0.0.18',
        'testtools>=1.4.0',
    ],
    zip_safe=True,
    entry_points={
        'console_scripts': [
            'laos-api = laos.service.laos_api:server',
        ]
    },

)
