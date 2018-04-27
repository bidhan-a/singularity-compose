import time
import json
import requests
from six import moves


class Singularity:
    def __init__(self, config):
        self.config = config

    def create_request_body(self):
        request_body = {
            "id": self.config['container_name'],
            "owners": [self.config.get('singularity_email', '')],
            "rackSensitive": False,
            "loadBalanced": False,
            "skipHealthchecks": True,
            "requestType": "SERVICE",
            "requiredSlaveAttributes": self.config.get('host_attributes', {})
        }

        if self.config['slave_placement']:
            request_body['slavePlacement'] = self.config.get('slave_placement', '')

        if self.config["cron_schedule"]:
            request_body['schedule'] = self.config.get('cron_schedule', '')
            request_body['scheduleType'] = 'CRON'
            request_body['requestType'] = 'SCHEDULED'

        return request_body

    def create_deploy_body(self):
        deploy_body = {
            "requestId": self.config['container_name'],
            "unpauseOnSuccessfulDeploy": True,
            "message": "Initiated by {}".format(self.config.get('singularity_email', '')),
            "deploy": {
                "requestId": self.config['container_name'],
                "id":  "",
                "command": self.config.get('entrypoint', None),  # set command equal to entrypoint
                "arguments": self.config.get("arguments", []),
                "containerInfo": {
                    "type": "DOCKER",
                    "volumes": self.config.get('volumes', []),
                    "docker": {
                        "forcePullImage": self.config.get("force_pull_image", False),
                        "privileged": self.config.get("privileged", False),
                        "network": self.config["network_mode"],
                        "portMappings": self.config["port_mappings"],
                        "image": self.config["image"],
                        "parameters": self.config.get("docker_params", {})
                    }
                },
                "hostname": self.config["container_name"],
                "env": self.config.get('environment', {}),
                "resources": {
                    "cpus": self.config.get('cpus', ''),
                    "memoryMb": self.config.get('memory', ''),
                    "diskMb": self.config.get('disk', ''),
                    "numPorts": self.config.get('num_ports', '') or 1
                },
                "skipHealthchecksOnDeploy": True
            }
        }
        return deploy_body

    def deploy(self):
        endpoint = self.config.get('singularity_endpoint', '')
        container_name = self.config["container_name"]
        deploy_id = str(int(time.time()))

        yn = moves.input("Are you sure, you want to deploy '{}' Singularity (y/n)? ".format(container_name))
        yn = yn.lower()
        if yn not in ['yes', 'y']:
            return False

        print("Creating deploy request for '{}'".format(container_name))
        request_body = self.create_request_body()
        print(json.dumps(request_body, indent=4))

        resp = requests.post(endpoint + '/requests', data=json.dumps(request_body),
                             headers={'Content-Type': 'application/json'})

        if resp and resp.status_code == 200:
            status_code = 400
            print("Deploying '{}'..".format(deploy_id))
            deploy_body = self.create_deploy_body()
            deploy_body['deploy']['id'] = deploy_id
            print(json.dumps(deploy_body, indent=4))
            while status_code != 200:
                time.sleep(2)
                resp = requests.post(endpoint + '/deploys', data=json.dumps(deploy_body),
                                     headers={'Content-Type': 'application/json'})
                status_code = resp.status_code

            print("Deployed '{}' successfully.".format(deploy_id))
            print(json.dumps(resp.json(), indent=4))
