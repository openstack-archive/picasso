*****************************
Picasso deployment guide
*****************************


DevStack
########

See full install guide in devstack_plugin_

Existing OpenStack
##################

Required software::

* Python 3.5 or greater
* Go 1.7 or greater
* Glide
* OpenStack Identity (Keystone)
* Docker (single instance or clustered)

Software that will be installed::

* IronFunctions
* Picasso


IronFunctions installation
**************************

IronFunctions is a core component of Picasso that interacts with the Docker API.

Run the following commands to install IronFunctions::

    export GOPATH=~/go
    export FUNCTIONS_DIR=$GOPATH/src/github.com/iron-io/functions
    mkdir -p $FUNCTIONS_DIR
    pushd $FUNCTIONS_DIR && GOPATH=${GOPATH} make all; popd

Running ``$FUNCTIONS_DIR/functions`` will start IronFunctions using an embedded Bolt database running on port 8080.

See IronFunctions configuration options_

Installing Picasso
******************

Picasso is a lightweight ReST API service to work with IronFunctions using the OpenStack Identity (Keystone) model.


Run the following commands to install Picasso::


    git clone git@github.com:iron-io/picasso.git
    pip3 install -r requirements.txt
    pip3 install -e .

Review the Picasso README_ for how to get started.

OpenStack Identity (Keystone) configuration
*******************************************

Create a new ``functions`` service in Keystone using the OpenStack_CLI_
This will enable the Picasso API by resolving its endpoint through the service catalog.

Running IronFunctions in production
***********************************

From a deployment perspective IronFunctions is nothing more than an internal service, so its API should not be exposed to OpenStack users.

Running Picasso in production
*****************************

Required software::

    Load balancer such as HaProxy or Nginx


The Picasso API endpoint should be available to OpenStack users, therefore it is suggested to run the API behind a load balancer.

.. _devstack_plugin: https://github.com/iron-io/picasso/blob/master/devstack/README.rst
.. _Glide: https://github.com/Masterminds/glide
.. _options: https://github.com/iron-io/functions/blob/master/docs/options.md
.. _README: https://github.com/iron-io/picasso/blob/master/README.md
.. _OpenStack_CLI: http://docs.openstack.org/cli-reference/