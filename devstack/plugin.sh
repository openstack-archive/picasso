#!/bin/bash
#

# lib/functions
# Functions to control the configuration and operation of the **Functions-as-a-Service** service

# Dependencies:
# ``functions`` file
# ``DEST``, ``STACK_USER`` must be defined
# ``SERVICE_{HOST|PROTOCOL|TOKEN}`` must be defined

# ``stack.sh`` calls the entry points in this order:
#


# Save trace setting
XTRACE=$(set +o | grep xtrace)
set +o xtrace

# Functions
# ---------


function is_functions_enabled {
    [[ ,${ENABLED_SERVICES} =~ ,"picasso" ]] && return 0
    return 1
}

function create_functions_accounts {
    if [[ "$ENABLED_SERVICES" =~ "functions" ]]; then

        create_service_user "picasso" "admin"

        local functions_service=$(get_or_create_service "picasso" \
            "functions" "Functions-as-a-Service")
        get_or_create_endpoint $functions_service \
            "$REGION_NAME" \
            "http://$SERVICE_HOST:$PICASSO_PORT" \
            "http://$SERVICE_HOST:$PICASSO_PORT" \
            "http://$SERVICE_HOST:$PICASSO_PORT"
    fi
}

function install_go_1.7.1 {
    wget https://storage.googleapis.com/golang/go1.7.linux-amd64.tar.gz -O /tmp/go1.7.linux-amd64.tar.gz
    sudo tar -xvf /tmp/go1.7.linux-amd64.tar.gz -C /usr/local/
    sudo rm -fr /usr/bin/go
    sudo rm -fr /usr/bin/gofmt
    sudo ln -s /usr/local/go/bin/go /usr/bin/go
    sudo ln -s /usr/local/go/bin/gofmt /usr/bin/gofmt
    `which go` env
}

function check_docker {
    if is_ubuntu; then
       dpkg -s docker-engine > /dev/null 2>&1
    else
       rpm -q docker-engine > /dev/null 2>&1
    fi
}

function install_docker {
    check_docker || curl -fsSL https://get.docker.com/ | sudo sh

    echo "Adding ${STACK_USER} to ${docker_group}..."
    add_user_to_group $STACK_USER $DOCKER_GROUP
    echo "Adding $(whoami) to ${DOCKER_GROUP}..."
    add_user_to_group $(whoami) $DOCKER_GROUP

    if is_fedora; then
        install_package socat dnsmasq
    fi

    if is_ubuntu && [ $UBUNTU_RELEASE_BASE_NUM -le 14 ]; then
        sudo service docker start || true
    else
        echo -e "[Unit]
    Description=Docker Application Container Engine
    Documentation=https://docs.docker.com
    After=network.target docker.socket
    Requires=docker.socket
    [Service]
    Type=notify
    Environment=SERVICE_HOST=${SERVICE_HOST}
    ExecStart=/usr/bin/dockerd -H tcp://${SERVICE_HOST}:2375 ${DOCKERD_OPTS}
    MountFlags=slave
    LimitNOFILE=1048576
    LimitNPROC=1048576
    LimitCORE=infinity
    TimeoutStartSec=0
    Delegate=yes
    [Install]
    WantedBy=multi-user.target" | sudo tee -a /lib/systemd/system/docker.service.new

        sudo mv /lib/systemd/system/docker.service.new /lib/systemd/system/docker.service

        sudo systemctl daemon-reload
        sudo systemctl enable docker.service
        sudo systemctl restart docker || true
    fi
}


function is_glide_installed {
    echo_summary "Attempting to find Glide binary"
    local glbin=`which glide`
    if [[ -z "${glbin}" ]]; then
        echo_summary "Glide is not installed, aborting."
        exit 1
    fi
}


function install_picasso {
    echo_summary "Installing Picasso"
    git_clone $PICASSO_REPO $PICASSO_DIR $FUNCTIONS_BRANCH
    pushd $PICASSO_DIR && docker -H tcp://${SERVICE_HOST}:2375 build -t picasso-api -f $PICASSO_DIR/Dockerfile .; popd
}

function apply_picasso_migrations {
    echo_summary "Applying Picasso migrations"
    recreate_database_mysql functions
    local picasso_db=$(get_database_type_mysql)://${DATABASE_USER}:${DATABASE_PASSWORD}@${MYSQL_HOST}/functions
    pushd $PICASSO_DIR && PICASSO_MIGRATIONS_DB=${picasso_db} alembic upgrade head; popd

}

function install_functions {
    echo_summary "Pulling Functions sources"
    git_clone $FUNCTIONS_REPO $GOPATH/src/github.com/iron-io/functions $FUNCTIONS_BRANCH
    pushd $FUNCTIONS_DIR && GOPATH=${GOPATH} make all; popd
}

function configure_systemctl_for_functions_api {
    echo -e "[Unit]
Description=Functions API service
After=network.target
[Service]
Type=notify
Environment=GOPATH=${GOPATH}
Environment=PORT=${FUNCTIONS_PORT}
Environment=API_URL=http://${SERVICE_HOST}:${FUNCTIONS_PORT}
Environment=DOCKER_HOST=tcp://${SERVICE_HOST}:2375
Environment=LOG_LEVEL=${FUNCTIONS_LOG_LEVEL}
Environment=DB_URL=${FUNCTIONS_DB}
Environment=MQ_URL=${FUNCTIONS_MQ}
ExecStart=${FUNCTIONS_DIR}/functions
LimitNOFILE=1048576
LimitNPROC=1048576
LimitCORE=infinity
TimeoutStartSec=0
[Install]
WantedBy=multi-user.target" | sudo tee - a /lib/systemd/system/functions-api.service.new

    sudo mv /lib/systemd/system/functions-api.service.new /lib/systemd/system/functions-api.service
    sudo systemctl daemon-reload
}

function configure_systemctl_for_picasso_api {
    rm -fr $PICASSO_DIR/.picasso.docker
    echo -e "PICASSO_HOST=0.0.0.0
PICASSO_PORT=${PICASSO_PORT}
PICASSO_DB=$(get_database_type_mysql)://${DATABASE_USER}:${DATABASE_PASSWORD}@${SERVICE_HOST}/functions
KEYSTONE_ENDPOINT=http://${SERVICE_HOST}:5000/v3
FUNCTIONS_URL=http://${SERVICE_HOST}:${FUNCTIONS_PORT}/v1
PICASSO_LOG_LEVEL=DEBUG
    " | tee -a $PICASSO_DIR/.picasso.docker

    echo -e "[Unit]
Description=Picasso API service
After=network.target
[Service]
Type=notify
Environment=PICASSO_DIR=${PICASSO_DIR}
Environment=DOCKER_HOST=tcp://${SERVICE_HOST}:2375
ExecStart=/usr/bin/docker -H tcp://${SERVICE_HOST}:2375 run --name picasso-api -d -p ${SERVICE_HOST}:10001:10001 --env-file ${PICASSO_DIR}/.picasso.docker picasso-api
ExecStop=/usr/bin/docker -H tcp://${SERVICE_HOST}:2375 stop -t 1 picasso-api
ExecStopPost=/usr/bin/docker -H tcp://${SERVICE_HOST}:2375 rm -f picasso-api
RemainAfterExit=true
LimitNOFILE=1048576
LimitNPROC=1048576
LimitCORE=infinity
TimeoutStartSec=0
[Install]
WantedBy=multi-user.target" | sudo tee - a /lib/systemd/system/picasso-api.service.new

    sudo mv /lib/systemd/system/picasso-api.service.new /lib/systemd/system/picasso-api.service
    sudo systemctl daemon-reload
}


function start_picasso_api {
    echo_summary "Starting Picasso API"
    sudo systemctl start picasso-api.service
}


function stop_picasso_api {
    echo_summary "Stopping Picasso API"
    sudo systemctl stop picasso-api.service
}


function start_functions {
    echo_summary "Starting Functions API"
    sudo systemctl start functions-api.service &
}


function stop_functions {
    echo_summary "Stopping Functions API"
    sudo systemctl stop functions-api.service &
}

function install_python_picassoclient {
    git_clone $PICASSO_CLIENT_REPO $PICASSO_CLIENT_DIR $PICASSO_CLIENT_BRANCH
    setup_develop $PICASSO_CLIENT_DIR
}

if is_service_enabled functions; then

    if [[ "$1" == "stack" && "$2" == "install" ]]; then
        echo_summary "Installing Functions"
        install_docker
        install_go_1.7.1
        is_glide_installed
        install_functions
        install_picasso
        install_python_picassoclient
    elif [[ "$1" == "stack" && "$2" == "post-config" ]]; then
        echo_summary "Configuring Picasso and IronFunctions"
        configure_systemctl_for_functions_api
        configure_systemctl_for_picasso_api
        if is_service_enabled key; then
            create_functions_accounts
        fi
    elif [[ "$1" == "stack" && "$2" == "extra" ]]; then
        apply_picasso_migrations
        start_functions
        start_picasso_api
    fi

    if [[ "$1" == "unstack" ]]; then
        stop_functions
        stop_picasso_api
    fi
fi

# Restore xtrace
$XTRACE
