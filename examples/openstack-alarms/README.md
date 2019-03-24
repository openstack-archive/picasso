## Integrating OpenStack Telemetry alarming with Picasso


OpenStack Aodh is the alarming service for OpenStack Telemetry.
The Ceilometer service collects and transforms data from OpenStack services.
Using Aodh, users/operators are able to setup alarms to trigger based on custom rules.

### Deploying DevStack

To see how Aodh can be integrated with Picasso, we recommend using DevStack as the simplest and fastest way to get both Aodh and Picasso services running along with Nova, Glance and Neutron services.
In order to get DevStack use following commands:

```bash
export DEVSTACK_DIR=~/devstack
git clone https://git.openstack.org/openstack-dev/devstack.git $DEVSTACK_DIR
```

Create a file, `$DEVSTACK_DIR/local.conf` with the following text:

```bash
[[local|localrc]]

enable_plugin aodh https://git.openstack.org/openstack/aodh
enable_plugin picasso git@github.com:openstack/picasso.git

# Picasso configuration
PICASSO_REPO=${PICASSO_REPO:-git@github.com:openstack/picasso.git}
PICASSO_BRANCH=${PICASSO_BRANCH:-master}
PICASSO_DIR=${PICASSO_DIR:-${DEST}/picasso}
PICASSO_PORT=${PICASSO_PORT:-10001}
PICASSO_LOG_LEVEL=${PICASSO_LOG_LEVEL:-DEBUG}
PICASSO_LOG_FILE=${PICASSO_LOG_FILE:-/var/log/picasso-api.log}

# Picasso client configuration
PICASSO_CLIENT_REPO=${PICASSO_CLIENT_REPO:-git@github.com:openstack/python-picassoclient.git}
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
```

Start DevStack installation

```bash
./stack.sh
```

### Creating app and route


Once DevStack is installed, create a Picasso app:

```bash
openstack fn apps create alarm-notifier-app

+-------------+--------------------------------------------------+
| Field       | Value                                            |
+-------------+--------------------------------------------------+
| name        | alarm-notifier-app-f6fdaab020e                   |
| created_at  | 2016-12-12 18:08:26.077455                       |
| updated_at  | 2016-12-12 18:08:26.077477                       |
| project_id  | f6fdaab020ec4cdf85db3740520ec658                 |
| config      | None                                             |
| id          | f012ff74ea1c43b6a12c3c946fe96de5                 |
| description | App for project f6fdaab020ec4cdf85db3740520ec658 |
+-------------+--------------------------------------------------+
```

Create a route:
```bash
openstack fn routes create alarm-notifier-app-f6fdaab020e /hello async iron/hello --is-public

+-----------------+------------+
| Field           | Value      |
+-----------------+------------+
| image           | iron/hello |
| memory          | 128        |
| max_concurrency | 1          |
| timeout         | 30         |
| path            | /hello     |
| is_public       | True       |
| type            | async      |
+-----------------+------------+
```

Bootstrap VM on cirros image:
```bash
nova boot --image $(glance image-list | awk '/cirros-0.3.4-x86_64-uec / {print $2}') --flavor 42 test_alarms

+--------------------------------------+----------------------------------------------------------------+
| Property                             | Value                                                          |
+--------------------------------------+----------------------------------------------------------------+
| OS-DCF:diskConfig                    | MANUAL                                                         |
| OS-EXT-AZ:availability_zone          |                                                                |
| OS-EXT-STS:power_state               | 0                                                              |
| OS-EXT-STS:task_state                | scheduling                                                     |
| OS-EXT-STS:vm_state                  | building                                                       |
| OS-SRV-USG:launched_at               | -                                                              |
| OS-SRV-USG:terminated_at             | -                                                              |
| accessIPv4                           |                                                                |
| accessIPv6                           |                                                                |
| adminPass                            | C9bfvqY4p3Lz                                                   |
| config_drive                         |                                                                |
| created                              | 2016-12-12T22:17:56Z                                           |
| description                          | -                                                              |
| flavor                               | m1.nano (42)                                                   |
| hostId                               |                                                                |
| id                                   | 7a4822c5-9fd4-44af-a54e-daef65650ca7                           |
| image                                | cirros-0.3.4-x86_64-uec (b60ad91d-2917-46b2-881c-0c5a277c6f8d) |
| key_name                             | -                                                              |
| locked                               | False                                                          |
| metadata                             | {}                                                             |
| name                                 | test_alarms                                                    |
| os-extended-volumes:volumes_attached | []                                                             |
| progress                             | 0                                                              |
| security_groups                      | default                                                        |
| status                               | BUILD                                                          |
| tags                                 | []                                                             |
| tenant_id                            | f6fdaab020ec4cdf85db3740520ec658                               |
| updated                              | 2016-12-12T22:17:56Z                                           |
| user_id                              | d0ec76f99e3c4e588119c8f6858a4ba3                               |
+--------------------------------------+----------------------------------------------------------------+
```

Create Aodh alarm:

```bash
aodh alarm create \
    --type threshold \
    --name cpu_high \
    --description 'instance running hot' \
    --meter-name cpu_util \
    --threshold 20.0 \
    --comparison-operator gt \
    --statistic max \
    --period 600 \
    --evaluation-periods 1 \
    --alarm-action $(openstack fn routes expose-url testapp-f6fdaab020ec4cdf85db37 /hello) \
    --query resource_id=$(nova list | grep test_alarms | awk '{print $2}')

+---------------------------+------------------------------------------------------------------------+
| Field                     | Value                                                                  |
+---------------------------+------------------------------------------------------------------------+
| alarm_actions             | [u'http://192.168.0.114:10001/r/testapp-f6fdaab020ec4cdf85db37/hello'] |
| alarm_id                  | f3460bad-2b5c-4c2f-b6e0-e82973e6ec71                                   |
| comparison_operator       | gt                                                                     |
| description               | instance running hot                                                   |
| enabled                   | True                                                                   |
| evaluation_periods        | 1                                                                      |
| exclude_outliers          | False                                                                  |
| insufficient_data_actions | []                                                                     |
| meter_name                | cpu_util                                                               |
| name                      | cpu_high                                                               |
| ok_actions                | []                                                                     |
| period                    | 600                                                                    |
| project_id                | f6fdaab020ec4cdf85db3740520ec658                                       |
| query                     | resource_id = 7a4822c5-9fd4-44af-a54e-daef65650ca7 AND                 |
|                           | project_id = f6fdaab020ec4cdf85db3740520ec658                          |
| repeat_actions            | False                                                                  |
| severity                  | low                                                                    |
| state                     | insufficient data                                                      |
| state_timestamp           | 2016-12-12T22:20:48.030596                                             |
| statistic                 | max                                                                    |
| threshold                 | 20.0                                                                   |
| time_constraints          | []                                                                     |
| timestamp                 | 2016-12-12T22:20:48.030596                                             |
| type                      | threshold                                                              |
| user_id                   | d0ec76f99e3c4e588119c8f6858a4ba3                                       |
+---------------------------+------------------------------------------------------------------------+
```

To trigger the alarm, generate CPU load on the provisioned VM:

```bash
ssh cirros@10.0.0.7
cirros@10.0.0.7 password: 
dd if=/dev/zero of=/dev/null
```

Once our threshold has been reached, Aodh will notify with an HTTP Callback to our async function assigned to the route we created.

### Conclusion
Picasso's ability to provide public sync/async function routes can be used to integrate with web hooks, such as Aodh, the OpenStack Telemetry alarming service.
