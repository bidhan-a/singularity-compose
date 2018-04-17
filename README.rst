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

singularity-compose supports four arguments:

- ``-c`` or ``--config`` : The name of the base compose file
- ``-s`` or ``--service`` : The name of the service to be deployed
- ``-o`` or ``--override``: The name of the compose file which overrides the base file
- ``-f`` or ``--forcepull``: Flag to enforce image pull (overrides the configuration in the compose file)

**Note**: You would use ``docker-compose`` with the above mentioned files as given below:

``docker-compose -f docker-compose.yml -f docker-compose.dev.yml up``


Singularity Options
-------------------

singularity-compose makes use of the ``labels`` option in the compose file
to pass different options to Singularity. The supported labels are given below:

- ``mesos.singularity.admin_email``
- ``mesos.singularity.endpoint``
- ``mesos.singularity.slave.placement``
- ``mesos.singularity.cron.schedule``
- ``mesos.singularity.docker.params``
- ``mesos.singularity.docker.forcepull``
- ``mesos.singularity.host.attributes``
- ``mesos.singularity.resources.cpus``
- ``mesos.singularity.resources.memory``
- ``mesos.singularity.resources.disk``
- ``mesos.singularity.resources.numports``

**Note**: ``mesos.singularity.docker.params`` and ``mesos.singularity.host.attributes`` are passed as objects.
The following example demonstrates how you can add properties to the object:

.. code-block:: python

   mesos.singularity.host.attributes.role = 'dev'
   mesos.singularity.host.attributes.other = 'extra'

This will create the following object:

.. code-block:: python

   {
       "role": "dev",
       "other": "extra"
   }

Refer to the docs on SingularityDeployRequest_ to learn more about the options.

.. _SingularityDeployRequest: https://github.com/HubSpot/Singularity/blob/master/Docs/reference/api.md#model-SingularityDeployRequest

