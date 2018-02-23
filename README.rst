===================
singularity-compose
===================


.. image:: https://img.shields.io/pypi/v/singularity-compose.svg
        :target: https://pypi.python.org/pypi/singularity-compose

.. image:: https://img.shields.io/travis/bidhan-a/singularity-compose.svg
        :target: https://travis-ci.org/bidhan-a/singularity-compose

.. image:: https://pyup.io/repos/github/bidhan-a/singularity-compose/shield.svg
     :target: https://pyup.io/repos/github/bidhan-a/singularity-compose/
     :alt: Updates



Deploy to Singularity with docker-compose files



Installation
------------

**singularity-compose** is available on PyPI. You can use pip to install it

``$ pip install singularity-compose``

Usage
-----

Once you have it installed, you can use it from the command line

``$ singularity-compose -c docker-compose.yml -s api -o docker-compose.dev.yml``

singularity-compose supports three arguments:

- ``-c`` or ``--config`` : The name of the base compose file
- ``-s`` or ``--service`` : The name of the service to be deployed
- ``-o`` or ``--override``: The name of the compose file which overrides the base file

**Note**: You would use ``docker-compose`` with the above mentioned files as given below:

``docker-compose -f docker-compose.yml -f docker-compose.dev.yml up``


Singularity Options
-------------------

singularity-compose makes use of the ``labels`` option in the compose file
to pass different options to Singularity. The supported labels are given below:

- ``mesos.singularity.admin_email``
- ``mesos.singularity.endpoint``
- ``mesos.slave.placement``
- ``mesos.cron.schedule``
- ``mesos.docker.params``
- ``mesos.docker.forcepull``
- ``mesos.docker.privileged``
- ``mesos.deploy.env``
- ``mesos.host.attributes``

**Note**: ``mesos.docker.params``, ``mesos.deploy.env``, and ``mesos.host.attributes`` are passed as objects.
The following example demonstrates how you can add properties to the object:

.. code-block:: python

   mesos.deploy.env.APP_ENV = 'dev'
   mesos.deploy.env.EXTRA_ENV = 'extra'

This will create the following object:

.. code-block:: python

   {
       "APP_ENV": "dev",
       "EXTRA_ENV": "extra"
   }

Refer to the docs on SingularityDeployRequest_ to learn more about the options.

.. _SingularityDeployRequest: https://github.com/HubSpot/Singularity/blob/master/Docs/reference/api.md#model-SingularityDeployRequest

