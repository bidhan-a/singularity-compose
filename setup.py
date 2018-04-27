#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = ['PyYAML', 'requests', 'six']

setup_requirements = ['pytest-runner', ]

test_requirements = ['pytest', ]

setup(
    author="Bidhan Adhikary",
    author_email='bidhan619@gmail.com',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    description="Deploy to multiple container platforms/PAAS using docker-compose files",
    entry_points={
      'console_scripts': ['compose-paas=compose_paas.main:deploy']
    },
    install_requires=requirements,
    license="BSD license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='compose-paas',
    name='compose-paas',
    packages=find_packages(include=['compose_paas', 'compose_paas.platform']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/bidhan-a/compose-paas',
    version='1.0.2',
    zip_safe=False,
)
