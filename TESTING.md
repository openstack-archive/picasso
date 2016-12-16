# Testing

## Requirements

* Install `Tox`

        $ pip install tox

* MySQL instance with database migrations applied (refer to quick start guide)

        $ export TEST_DB_URI=mysql://<your-user>:<your-user-password>@<mysql-host>:<mysql-port>/<functions-db>

### PEP8 style checks

    $ tox -e pep8


### Functional testing

    $ tox -e py35-functional

Pros:

* lightweight (controllers and DB models testing)
* no OpenStack required
* no IronFunctions required

Cons:

* MySQL server required
* OpenStack authentication is not tested
* IronFunctions API stubbed with fake implementation

### Integration tests

The following env variables are required:

* TEST_DB_URI - similar to functional tests, database endpoint
* FUNCTIONS_API_URL - IronFunctions API URL (default value - `http://localhost:8080/v1`)
* OS_AUTH_URL - OpenStack Identity endpoint
* OS_PROJECT_NAME - OpenStack user-specific project name
* OS_USERNAME - OpenStack user name
* OS_PASSWORD - OpenStack user user password

```bash
export TEST_DB_URI=mysql://<your-user>:<your-user-password>@<mysql-host>:<mysql-port>/<functions-db>
export FUNCTIONS_API_URL=<functions-api-protocol>://<functions-host>:<functions-port>/<functions-api-version>
export OS_AUTH_URL=<identity-api-protocol>://<identity-host>:<identity-port>/<identity-api-version>
export OS_PROJECT_NAME=<project-name>
export OS_USERNAME=<project-name>
export OS_PASSWORD=<project-name>
tox -epy35-integration
```

### Testing: Docker-build

The following operations are performed:

* builds an image
* deletes all artifacts (Python3.5 image and recently built image)

```bash
export DOCKER_HOST=tcp://<docker-host>:<docker-port>>
export TEST_DB_URI=mysql://<your-user>:<your-user-password>@<mysql-host>:<mysql-port>/<functions-db>
export FUNCTIONS_API_URL=<functions-api-protocol>://<functions-host>:<functions-port>/<functions-api-version>
export OS_AUTH_URL=<identity-api-protocol>://<identity-host>:<identity-port>/<identity-api-version>
tox -e docker-build
```

### Testing Docker-full

The following operations are performed:

* build container from source code
* run container with exposed ports
* request Swagger API doc to see if API is responsive
* destroy running container

```bash
export DOCKER_HOST=tcp://<docker-host>:<docker-port>>
export TEST_DB_URI=mysql://<your-user>:<your-user-password>@<mysql-host>:<mysql-port>/<functions-db>
export FUNCTIONS_API_URL=<functions-api-protocol>://<functions-host>:<functions-port>/<functions-api-version>
export OS_AUTH_URL=<identity-api-protocol>://<identity-host>:<identity-port>/<identity-api-version>
tox -e docker-full
```

### Coverage regression testing

    $ tox -e py35-functional-regression

### Static code analysis with Bandit

    $ tox -e bandit
