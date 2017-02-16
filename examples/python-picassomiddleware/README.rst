OpenStack Swift middleware for serverless functions
===================================================
In DevStack local.conf::

    enable_service s-proxy s-object s-container s-account
    enable_plugin picasso git@github.com:openstack/picasso.git master

this will enable Swift and Picasso inside DevStack

After DevStack use following commands::

    $ git clone https://github.com/denismakogon/serverless-functions-middleware.git
    $ pushd serverless-functions-middleware && sudo python setup.py install; popd

Install latest Swift python client::

    $ git clone https://github.com/openstack/python-swiftclient.git
    $ pushd python-swiftclient && sudo python setup.py install; popd

Modify Swift proxy conf by adding::

    [filter:functions_middleware]
    use = egg:functions#functions_middleware

In **[pipeline:main]** section add **functions_middleware** to the list of other middleware in **pipeline** config option
Restart Swift proxy service by::

    screen -x
    restart s-proxy process

Create a function::

    $ openstack fn apps create testapp
    $ openstack fn routes create testapp-1445cef51c68427da92621 /hello sync iron/hello --is-public
    $ swift post test_container
    $

In Swift while uploading a file specify **X-FUNCTION-URL** that can be retrieved using expose-url command::

    $ openstack fn routes expose-url testapp-1445cef51c68427da92621 /hello
    $ swift upload test_container file --header "X-FUNCTION-URL:$(openstack fn routes expose-url testapp-1445cef51c68427da92621 /hello)"

A function that is being used would be supplied with X-AUTH-URL, X-PROJECT-ID and all relevant data about container and a file that is being upload.
