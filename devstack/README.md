# Enabling Picasso (Functions-as-a-Service) in DevStack

## Install Glide

It is required to install Glide on the system in which you plan to run DevStack on, as
the Functions service is written in Go and we must fetch dependencies during install.
See more info at https://github.com/Masterminds/glide


## Download DevStack

    export DEVSTACK_DIR=~/devstack
    git clone git://git.openstack.org/openstack-dev/devstack.git $DEVSTACK_DIR

## Enable the Functions plugin

Enable the plugin by adding the following section to ``$DEVSTACK_DIR/local.conf``

    [[local|localrc]]

    enable_plugin picasso git@github.com:iron-io/picasso.git

    # Picasso configuration
    PICASSO_REPO=${PICASSO_REPO:-git@github.com:iron-io/picasso.git}
    PICASSO_BRANCH=${PICASSO_BRANCH:-master}
    PICASSO_DIR=${PICASSO_DIR:-${DEST}/picasso}
    PICASSO_PORT=${PICASSO_PORT:-10001}
    PICASSO_LOG_LEVEL=${PICASSO_LOG_LEVEL:-DEBUG}
    PICASSO_LOG_FILE=${PICASSO_LOG_FILE:-/var/log/picasso-api.log}

    # Picasso client configuration
    PICASSO_CLIENT_REPO=${PICASSO_CLIENT_REPO:-git@github.com:iron-io/python-picassoclient.git}
    PICASSO_CLIENT_DIR=${PICASSO_CLIENT_DIR:-${DEST}/python-picassoclient}
    PICASSO_CLIENT_BRANCH=${PICASSO_CLIENT_BRANCH:-master}

    # Functions parameters
    FUNCTIONS_REPO=${FUNCTIONS_REPO:-git@github.com:iron-io/functions.git}
    FUNCTIONS_BRANCH=${FUNCTIONS_BRANCH:-master}
    FUNCTIONS_PORT=${FUNCTIONS_PORT:-10501}
    FUNCTIONS_DB=${FUNCTIONS_DBPATH:-bolt://$FUNCTIONS_DIR/devstack.functions.storage.db?bucket=funcs}
    FUNCTIONS_MQ=${FUNCTIONS_DBPATH:-bolt://$FUNCTIONS_DIR/devstack.functions.queue.db}
    FUNCTIONS_LOG_LEVEL=${FUNCTIONS_LOG_LEVEL:-DEBUG}

    DOCKERD_OPTS=${DOCKERD_OPTS:---dns 8.8.8.8 --dns 8.8.4.4 --storage-driver=overlay2 -H fd://}

## Run the DevStack utility

     cd $DEVSTACK_DIR
     ./stack.sh
