============
compose-paas
============


.. image:: https://img.shields.io/pypi/v/compose-paas.svg
        :target: https://pypi.python.org/pypi/compose-paas

.. image:: https://img.shields.io/travis/bidhan-a/compose-paas.svg
        :target: https://travis-ci.org/bidhan-a/compose-paas

.. image:: https://pyup.io/repos/github/bidhan-a/compose-paas/shield.svg
     :target: https://pyup.io/repos/github/bidhan-a/compose-paas/
     :alt: Updates



Deploy to multiple container platforms/PAAS using docker-compose files



Installation
------------

**compose-paas** is available on PyPI. You can use pip to install it

``$ pip install compose-paas``

Usage
-----

Once you have it installed, you can use it from the command line

``$ compose-paas -c docker-compose.yml -s api -o docker-compose.dev.yml -f true -p singularity``

compose-paas supports five arguments:

- ``-c`` or ``--config`` : The name of the base compose file
- ``-s`` or ``--service`` : The name of the service to be deployed
- ``-o`` or ``--override``: The name of the compose file which overrides the base file
- ``-f`` or ``--forcepull``: Flag to enforce image pull (overrides the configuration in the compose file)
- ``-p`` or ``--platform``: Platform to deploy to (currently, only singularity and marathon are supported)

**Note**: You would use ``docker-compose`` with the above mentioned files as given below:

``docker-compose -f docker-compose.yml -f docker-compose.dev.yml up``


Options
-------

compose-paas uses the `x-compose-paas` extension field in the docker-compose file
to read platform-specific as well as other general options. The following example
contains all the supported options:

.. code-block:: python

    x-compose-paas:
      resources:
        cpus: '0.1'
        memory: '1024'
      singularity:
        admin_email: 'admin@mail.com'
        endpoint: 'http://prd.net/singularity/api'
        slave_placement: ''
        cron_schedule: ''
      marathon:
        endpoint: 'http://prd.net/marathon/v2'
        fetch:
          uri: 'file:///etc/docker.tar.gz'
          resource_roles:
            - '*'
        id: '/service/name'
      docker:
        params:
          entrypoint: 'run_web_api.sh'
          ulimit: 'nofile=10240:10240'
        forcepull: 'false'


References
----------

- SingularityDeployRequest_
- `Marathon Configuration Reference`_

.. _SingularityDeployRequest: https://github.com/HubSpot/Singularity/blob/master/Docs/reference/api.md#model-SingularityDeployRequest
.. _Marathon Configuration Reference: https://docs.mesosphere.com/1.11/deploying-services/marathon-parameters/

