*********
Functions
*********


Writing functions
*****************

What is a function?
###################

Functions are small, bite sized bits of code that do one simple thing. Forget about
monoliths when using functions, just focus on the task that you want the function to perform.

Unlike an app/API/microservice that consumes resources 24/7 whether they are in use or not,
functions are time sliced across your infrastructure and only consume resources while they are
actually doing something.

Function composition
#####################
At a high-level, functions are comprised of applications and routes::

    An application is essentially a grouping of functions, that put together, form an API.

    A route is a way to define a path in your application that maps to a function.

Calling your function is as simple as requesting a URL. Each app has it's own namespace and
each route mapped to the app.

How are functions packaged?
###########################

Packaging a function has two parts:

Create a Docker image for your function with an ``ENTRYPOINT``::

    Push your Docker image to a registry (Docker Hub by default).
    
    Once it's pushed to a registry, you can use it by referencing it when adding a route.

Writing functions
#################

See the IronFunctions guide_ on writing functions.

What functions can do
######################

As functions are essentially just containers, anything that runs in a container can be a function.
Functions typically useful for short-lived tasks, such as:

    * Data processing
    * ETL


What functions cannot do
########################

Long running processes are not intended for functions.


.. _guide: https://github.com/iron-io/functions/blob/master/docs/writing.md