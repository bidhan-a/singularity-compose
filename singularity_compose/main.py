# -*- coding: utf-8 -*-

"""Main module."""
import argparse
import json
import requests
import time
from six import moves
from singularity_compose.config import Config
import pprint


def deploy():
    parser = argparse.ArgumentParser(description='Configuration options')
    parser.add_argument('-c', '--config', metavar='config', type=str,
                        help='The base compose file', required=True)
    parser.add_argument('-s', '--service', metavar='service', type=str,
                        help='Service name in the compose file', required=True)
    parser.add_argument('-o', '--override', metavar='override', type=str,
                        help='The compose file which overrides the base file', required=False)
    args = parser.parse_args()

    try:
        config = Config(config_file=args.config, service_name=args.service, override_file=args.override)
    except IOError as e:
        print('Compose file could not be loaded')
        print(str(e))
        config = None
    except Exception as e:
        print(str(e))
        config = None

    if config:
        endpoint = config.get('singularity_endpoint', '')
        admin = config.get('singularity_email', '')
        deploy_id = str(int(time.time()))

        request_body = {
            "id": config['container_name'],
            "owners": [admin],
            "rackSensitive": False,
            "loadBalanced": False,
            "skipHealthchecks": True,
            "requestType": "SERVICE",
            "requiredSlaveAttributes": config.get('host_attributes', {})
        }

        if config['slave_placement']:
            request_body['slavePlacement'] = config.get('slave_placement', '')

        if config["cron_schedule"]:
            request_body['schedule'] = config.get('cron_schedule', '')
            request_body['scheduleType'] = 'CRON'
            request_body['requestType'] = 'SCHEDULED'

        deploy_body = {
            "requestId": config['container_name'],
            "unpauseOnSuccessfulDeploy": True,
            "message": "Initiated by {}".format(admin),
            "deploy": {
                "requestId": config['container_name'],
                "id": deploy_id,
                "command": config.get('command', None),
                "arguments": config.get("arguments", []),
                "containerInfo": {
                    "type": "DOCKER",
                    "volumes": config.get('volumes', []),
                    "docker": {
                        "forcePullImage": config.get("force_pull_image", False),
                        "privileged": config.get("privileged", False),
                        "network": config["network_mode"],
                        "portMappings": config["portMappings"],
                        "image": config["image"],
                        "parameters": config.get("docker_params", {})
                    }
                },
                "hostname": config["container_name"],
                "env": config.get('environment', {}),
                "resources": {
                    "cpus": config.get('cpus', ''),
                    "memoryMb": config.get('memory', ''),
                    "diskMb": config.get('disk', ''),
                    "numPorts": config.get('num_ports', '') or 1
                },
                "skipHealthchecksOnDeploy": True
            }
        }

        pprint.pprint(request_body, indent=4)
        pprint.pprint(deploy_body, indent=4)
        yn = moves.input("Are you sure, you want to deploy '{}' (y/n)? ".format(config["container_name"]))
        yn = yn.lower()
        if yn not in ['yes', 'y']:
            return

        print("Creating deploy request for '{}'".format(config["container_name"]))
        print(json.dumps(request_body, indent=4))

        resp = requests.post(endpoint + '/requests', data=json.dumps(request_body),
                             headers={'Content-Type': 'application/json'})

        if resp and resp.status_code == 200:
            status_code = 400
            print("Deploying '{}'..".format(deploy_id))
            print(json.dumps(deploy_body, indent=4))
            while status_code != 200:
                time.sleep(2)
                resp = requests.post(endpoint + '/deploys', data=json.dumps(deploy_body),
                                     headers={'Content-Type': 'application/json'})
                status_code = resp.status_code

            print("Deployed '{}' successfully.".format(deploy_id))
            print(json.dumps(resp.json(), indent=4))
