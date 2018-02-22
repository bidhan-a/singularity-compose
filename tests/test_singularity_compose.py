#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `singularity-compose` package."""
import os
import pytest


from singularity_compose.config import Config


@pytest.fixture
def response():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')


def test_config(response):
    config_file = os.path.join(response, 'docker-compose.yml')
    override_file = os.path.join(response, 'docker-compose.dev.yml')

    config = Config(config_file=config_file, service_name='api', override_file=override_file)

    assert config.container_name == 'example-service'
    assert config.image == 'example/my_web_app:latest'

    # TODO: Add more assertions

