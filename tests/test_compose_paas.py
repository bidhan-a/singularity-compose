#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `compose-paas` package."""
import os
import pytest


from compose_paas.config import Config


@pytest.fixture
def response():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')


def test_config(response):
    config_file = os.path.join(response, 'docker-compose.yml')
    override_file = os.path.join(response, 'docker-compose.dev.yml')

    config = Config(config_file=config_file, platform='singularity', service_name='api', override_file=override_file)

    assert config.container_name == 'example-service'
    assert config.image == 'example/my_web_app:latest'
    assert config.force_pull_image is False

    assert config.environment == {'APP_ENV': 'dev', 'EXTRA_ENV': 'extra'}
    assert config.docker_params == {'entrypoint': 'run_web_api.sh', 'ulimit': 'nofile=10240:10240'}
    assert config.host_attributes == {'role': 'dev'}

    assert config.cpus == 0.1
    assert config.disk == 0.0
    assert config.memory == 1024.0
    assert config.num_ports == 0

    assert config.arguments == ['buildno=1']


