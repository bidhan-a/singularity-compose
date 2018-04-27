# -*- coding: utf-8 -*-

"""Main module."""
import argparse
from compose_paas.config import Config
from compose_paas.platform.singularity import Singularity
from compose_paas.platform.marathon import Marathon


def deploy():
    parser = argparse.ArgumentParser(description='Configuration options')
    parser.add_argument('-c', '--config', metavar='config', type=str,
                        help='The base compose file', required=True)
    parser.add_argument('-s', '--service', metavar='service', type=str,
                        help='Service name in the compose file', required=True)
    parser.add_argument('-p', '--platform', metavar='platform', type=str,
                        help='Platform to deploy to', required=True,
                        choices=['singularity', 'marathon'])
    parser.add_argument('-o', '--override', metavar='override', type=str,
                        help='The compose file which overrides the base file', required=False)
    parser.add_argument('-f', '--forcepull', metavar='forcepull', type=str,
                        help='Flag to enforce image pull', required=False)
    args = parser.parse_args()

    try:
        config = Config(config_file=args.config,
                        service_name=args.service,
                        platform=args.platform,
                        override_file=args.override,
                        force_pull=args.forcepull)
    except IOError as e:
        print('Compose file could not be loaded')
        print(str(e))
        config = None
    except Exception as e:
        print('Error in compose file')
        print(str(e))
        config = None

    if config:
        if args.platform == 'singularity':
            Singularity(config=config).deploy()
        elif args.platform == 'marathon':
            Marathon(config=config).deploy()
        else:
            print('Unsupported platform')
