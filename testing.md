Testing
-------

In order to run tests you need to install `Tox`:

    $ pip install tox

Also, you will need a running MySQL instance with the database migrations applied from the previous step.
Tests are dependent on pre-created MySQL database for persistence.
Please set env var

    $ export TEST_DB_URI=mysql://<your-user>:<your-user-password>@<mysql-host>:<mysql-port>/<functions-db>

PEP8 style checks
-----------------

In order to run `PEP8` style checks run following command:

    $ tox -e pep8


Functional testing
------------------

In order to run `functional` tests run following command:

    $ tox -e py35-functional

Pros:

* lightweight (controllers and DB models testing)
* no OpenStack required
* no IronFunctions required

Cons:

* MySQL server required
* OpenStack authentication is not tested
* IronFunctions API stubbed with fake implementation

Integration integrations
------------------------

Integration tests are dependent on following env variables:

* TEST_DB_URI - similar to functional tests, database endpoint
* FUNCTIONS_API_URL - IronFunctions API URL (default value - `http://localhost:8080/v1`)
* OS_AUTH_URL - OpenStack Identity endpoint
* OS_PROJECT_NAME - OpenStack user-specific project name
* OS_USERNAME - OpenStack user name
* OS_PASSWORD - OpenStack user user password

To run tests use following command:

    export TEST_DB_URI=mysql://<your-user>:<your-user-password>@<mysql-host>:<mysql-port>/<functions-db>
    export FUNCTIONS_API_URL=<functions-api-protocol>://<functions-host>:<functions-port>/<functions-api-version>
    export OS_AUTH_URL=<identity-api-protocol>://<identity-host>:<identity-port>/<identity-api-version>
    export OS_PROJECT_NAME=<project-name>
    export OS_USERNAME=<project-name>
    export OS_PASSWORD=<project-name>
    tox -epy35-integration

Testing: Docker-build
---------------------

This type of testing allows to ensure if code can be build inside docker container with no problems.
In order to run this check use following commands::

    export DOCKER_HOST=tcp://<docker-host>:<docker-port>>
    export TEST_DB_URI=mysql://<your-user>:<your-user-password>@<mysql-host>:<mysql-port>/<functions-db>
    export FUNCTIONS_API_URL=<functions-api-protocol>://<functions-host>:<functions-port>/<functions-api-version>
    export OS_AUTH_URL=<identity-api-protocol>://<identity-host>:<identity-port>/<identity-api-version>
    tox -e docker-build

During this check Tox:

* builds an image
* deletes all artifacts (Python3.5 image and recently built image)

Testing Docker-full
-------------------

This type of testing allows to ensure if code code can be build and run successfully inside docker container with no problems.
In order to run this check use following commands::

    export DOCKER_HOST=tcp://<docker-host>:<docker-port>>
    export TEST_DB_URI=mysql://<your-user>:<your-user-password>@<mysql-host>:<mysql-port>/<functions-db>
    export FUNCTIONS_API_URL=<functions-api-protocol>://<functions-host>:<functions-port>/<functions-api-version>
    export OS_AUTH_URL=<identity-api-protocol>://<identity-host>:<identity-port>/<identity-api-version>
    tox -e docker-full

During this check following operations are performed::

* build container from source code
* run container with exposed ports
* request Swagger API doc to see if API is responsive
* tear-down running container


Coverage regression testing
---------------------------

In order to build quality software it is necessary to keep test coverage at its highest point.
So, as part of `Tox` testing new check was added - functional test coverage regression.
In order to run it use following command:

    $ tox -e py35-functional-regression
