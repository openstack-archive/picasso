Project LaOS aka Lambdas-on-OpenStack
=====================================

Mission
-------

Provide capabilities to run software in "serverless" way.

Serverless
----------

Serverless is a new paradigm in computing that enables simplicity, 
efficiency and scalability for both developers and operators. 
It's important to distinguish the two, because the benefits differ:

Benefits for developers
-----------------------

The main benefits that most people refer to are on the developer side and they include:

* No servers to manage (serverless) -- you just upload your code and the platform deals with the infrastructure
* Super simple coding -- no more monoliths! Just simple little bits of code
* Pay by the milliseconds your code is executing -- unlike a typical application that runs 24/7, and you're paying
  24/7, functions only run when needed

Benefits for operators
----------------------

If you will be operating IronFunctions (the person who has to manage the servers behind the serverless),
then the benefits are different, but related.

* Extremely efficient use of resources
  * Unlike an app/API/microservice that consumes resources 24/7 whether they
    are in use or not, functions are time sliced across your infrastructure and only consume resources while they are
    actually doing something
* Easy to manage and scale
  * Single system for code written in any language or any technology
  * Single system to monitor
  * Scaling is the same for all functions, you don't scale each app independently
  * Scaling is simply adding more IronFunctions nodes

System requirements
-------------------

* Operating system: Linux/MacOS
* Python version: 3.5 or greater
* Database: MySQL 5.7 or greater

Quick-start guide
-----------------

Install DevStack with [IronFunctions enabled](https://github.com/iron-io/functions-devstack-plugin/blob/master/README.rst).
Pull down [Project LaOS sources](https://github.com/iron-io/project-laos).

Create Python3.5 virtualenv:

    $ virtualenv -p python3.5 .venv
    $ source .venv/bin/activate

Install dependencies:

    $ pip install -r requirements.txt -r test-requirements.txt

Install `functions_python` lib:

    $ pip install -e git+ssh://git@github.com/iron-io/functions_python.git#egg=functions-python

Install LaOS itself:

    $ pip install -e .


Migrations
----------

Once all dependencies are installed it is necessary to run database migrations.
Before that please edit [alembic.ini](alembic.ini) line #32

    sqlalchemy.url = mysql+pymysql://root:root@192.168.0.112/functions

In this section please specify connection URI to your own database.
Once it is done just hit alembic to apply migrations:

    $ alembic upgrade head

Starting a server
-----------------

Once it is finished you will have a console script `laos-api`:

    $ laos-api --help

    Usage: laos-api [OPTIONS]
    
      Starts an Project Laos API service
    
    Options:
      --host TEXT                    API service bind host.
      --port INTEGER                 API service bind port.
      --db-uri TEXT                  LaOS persistence storage URI.
      --keystone-endpoint TEXT       OpenStack Identity service endpoint.
      --functions-host TEXT          Functions API host
      --functions-port INTEGER       Functions API port
      --functions-api-version TEXT   Functions API version
      --functions-api-protocol TEXT  Functions API protocol
      --log-level TEXT               Logging file
      --log-file TEXT                Log file path
      --help                         Show this message and exit.

Minimum required options to start LaOS API service:

     --db-uri mysql://root:root@192.168.0.112/functions
     --keystone-endpoint http://192.168.0.112:5000/v3
     --functions-host 192.168.0.112
     --functions-port 10501
     --log-level INFO

Examining API
-------------

In [examples](examples/) folder you can find a script that examines available API endpoints, but this script relays on:

* `LAOS_API_URL` - Project LaOS API endpoint
* `OS_AUTH_URL` - OpenStack Auth URL
* `OS_PROJECT_ID` - it can be found in OpenStack Dashboard or in CLI

Along with that, you need to adjust [token_request.json](examples/token_request.json) in order to retrieve X-Auth-Token for further authentication against OpenStack and LaOS API service.

Then just run script:

    OS_AUTH_URL=http://192.168.0.112:5000/v3 OS_PROJECT_ID=8fb76785313a4500ac5367eb44a31677 ./hello-lambda.sh

Please note, that given values are project-specific, so they can't be reused.


TODOs
-----

* Create aiohttp swagger API using [aiohttp-swagger](https://github.com/cr0hn/aiohttp-swagger)
* Support app deletion in IronFunctions
* Support tasks listing/showing
* Tests: integration, functional, units
* better logging coverage
* Support logging instance passing in [function-python](https://github.com/iron-io/functions_python)
* python-laosclient (ReST API client and CLI tool)
* App writing examples


Contacts
--------

Feel free to reach us out at:

* [Slack channel](https://open-iron.herokuapp.com/)
* [Email](https://github.com/denismakogon)
