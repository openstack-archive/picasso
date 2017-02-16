Swift metering notification
===========================

DevStack configuration
----------------------

In order to get OpenStack Telemetry development box in it necessary to using following configuration to install
Panko as events system, Ceilometer as notifications system, Aodh as alarming system and Picasso as Functions-as-a-Service.

local.conf::

    [[local|localrc]]

    ADMIN_PASSWORD=root
    DATABASE_PASSWORD=root
    RABBIT_PASSWORD=root
    SERVICE_PASSWORD=root
    SERVICE_TOKEN=root

    enable_service s-proxy s-object s-container s-account

    enable_plugin panko https://git.openstack.org/openstack/panko
    enable_plugin ceilometer https://git.openstack.org/openstack/ceilometer
    enable_plugin aodh https://git.openstack.org/openstack/aodh

    enable_service aodh-evaluator aodh-notifier aodh-api
    disable_service ceilometer-alarm-notifier ceilometer-alarm-evaluator

    enable_plugin picasso git@github.com:openstack/picasso.git

By default Ceilometer DevStack plugin installs python-ceilometermiddleware for Swift as its proxy API middleware that sends notifications through message queue to a specific topic ("notifications" by default)

Configuring Ceilometer event pipeline
-------------------------------------

To enable this functionality, config the Ceilometer to be able to publish events to the queue the aodh-listener service listen on.
The event_alarm_topic config option of Aodh identify which messaging topic the aodh-listener on, the default value is “alarm.all”.
In Ceilometer side, a publisher of notifier type need to be configured in the event pipeline config file(**event_pipeline.yaml** as default),
the notifier should be with a messaging topic same as the event_alarm_topic option defined. For an example::

    ---
    sources:
        - name: event_source
          events:
              - "*"
          sinks:
              - event_sink
    sinks:
        - name: event_sink
          transformers:
          publishers:
              - notifier://
              - notifier://?topic=alarm.all


Collecting events from Swift
----------------------------

On each API request Swift emits (through python-ceilometermiddleware) notifications to a message queue.
Those notifications are being transformed into Ceilometer/Panko events and available via Ceilometer API.

Setting up alarms based on Swift notifications
----------------------------------------------

Once DevStack is installed, create a Picasso app::

    openstack fn apps create alarm-notifier-app

Create a route::

    openstack fn routes create alarm-notifier-app-5a3e626d281 /hello async iron/hello --is-public

After that setup Aodh alarm::

    aodh alarm create --event-type objectstore.http.request \
        --description objectstore_request --period 600 --evaluation-periods 1 \
        --alarm-action $(openstack fn routes expose-url alarm-notifier-app-5a3e626d281 /hello) \
        --name objectstore_request \
        --type event --ok-action $(openstack fn routes expose-url alarm-notifier-app-5a3e626d281 /hello)

This alarm would be triggered once **objectstore.http.request** event and one of the actions (alarm action or OK action) will be executed
by submitting POST request with event data.

In Aodh (aodh-notifier) logs we can see that event alarm URL is being triggered::

    2017-02-16 15:45:14.802 29717 DEBUG aodh.notifier [-] Received 1 messages in batch. sample /opt/stack/aodh/aodh/notifier/__init__.py:98
    2017-02-16 15:45:14.803 29717 DEBUG aodh.notifier [-] Notifying alarm 5a911a27-487c-49d4-a4da-68b209eda2cc with action SplitResult(scheme=u'http', netloc=u'192.168.0.114:10001', path=u'/r/alarm-notifier-app-5a3e626d281/hello', query='', fragment='') _handle_action /opt/stack/aodh/aodh/notifier/__init__.py:138
    2017-02-16 15:45:14.804 29717 INFO aodh.notifier.rest [-] Notifying alarm objectstore_request 5a911a27-487c-49d4-a4da-68b209eda2cc with severity low from insufficient data to alarm with action SplitResult(scheme=u'http', netloc=u'192.168.0.114:10001', path=u'/r/alarm-notifier-app-5a3e626d281/hello', query='', fragment='') because Event <id=52346005-00d3-4789-9347-1a29bdddde18,event_type=objectstore.http.request> hits the query <query=[]>.. request-id: req-cd265735-ef58-468d-aca3-65e3add9a03c
    2017-02-16 15:45:15.041 29717 INFO aodh.notifier.rest [-] Notifying alarm <5a911a27-487c-49d4-a4da-68b209eda2cc> gets response: 200 OK.

Also (in aodh-listener)::

    2017-02-16 15:56:57.542 29761 DEBUG aodh.evaluator.event [-] Evaluating event: event = {u'event_type': u'objectstore.http.request', u'traits': [[u'typeURI', 1, u'http://schemas.dmtf.org/cloud/audit/1.0/event'], [u'eventTime', 1, u'2017-02-16T13:56:54.322957'], [u'outcome', 1, u'success'], [u'user_id', 1, u'106a49d7d2fe4bc99792a3a95195b843'], [u'initiator_typeURI', 1, u'service/security/account/user'], [u'service', 1, u'ceilometermiddleware'], [u'target_id', 1, u'af2f24bca17e4d7f974c5a07012636db'], [u'observer_id', 1, u'target'], [u'initiator_id', 1, u'106a49d7d2fe4bc99792a3a95195b843'], [u'eventType', 1, u'activity'], [u'target_typeURI', 1, u'service/storage/object'], [u'action', 1, u'read'], [u'project_id', 1, u'04108819f6294723ba539b73b0c40a03'], [u'id', 1, u'b2552bc9-20ad-516c-a9ae-e58a7e016e82']], u'message_signature': u'364eec8d900cac2cc99679b5d171d279c32138114b93250e2954782d1f961c54', u'raw': {}, u'generated': u'2017-02-16T13:56:54.323449', u'message_id': u'6531d952-07f7-4534-aaf2-b6be3934f831'} evaluate_events /opt/stack/aodh/aodh/evaluator/event.py:167
    2017-02-16 15:56:57.543 29761 DEBUG aodh.evaluator.event [-] Finished event alarm evaluation. evaluate_events /opt/stack/aodh/aodh/evaluator/event.py:184

But the data that is being sent to a functions does not contain any useful information regarding actual resources that were modified, so no way to get the information on it.

Alternative
-----------

As part of Picasso distribution Swift middleware is available, see https://github.com/openstack/picasso/tree/master/examples/python-picassomiddleware
