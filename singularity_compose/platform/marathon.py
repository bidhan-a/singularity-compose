import json
import requests
from six import moves


class Marathon:
    def __init__(self, config):
        self.config = config

    def create_deploy_body(self):
        network_mode = self.config.get('network_mode')
        if network_mode == "bridge":
            network_mode = "container/bridge"

        docker_params = self.config.get("docker_params", {})
        parameters = []
        for k in docker_params:
            parameters.append({
                "key": k,
                "value": docker_params[k]
            })

        host_attributes = self.config.get('host_attributes', {})
        constraints = []
        for k in host_attributes:
            constraints.append([k, 'IS', host_attributes[k]])

        cmd = self.config.get('entrypoint', '')
        args = self.config.get('arguments', [])

        deploy_body = {
            "id": self.config['marathon_id'],
            "container": {
                "type": "DOCKER",
                "volumes": self.config.get('volumes', []),
                "docker": {
                    "image": self.config["image"],
                    "privileged": self.config.get("privileged", False),
                    "forcePullImage": self.config.get("force_pull_image", False),
                    "parameters": parameters
                },
                "portMappings": self.config["port_mappings"],
            },
            "cpus": self.config.get('cpus', ''),
            "mem": self.config.get('memory', ''),
            "disk": self.config.get('disk', ''),
            "requirePorts": False,
            "networks": [
                {
                    "mode": network_mode
                }
            ],
            "fetch": [self.config.get('marathon_fetch', {})],
            "constraints": constraints,
            "env": self.config.get('environment', {}),
            "acceptedResourceRoles": self.config.get('marathon_resource_roles', [])
        }

        # There can be either args or cmd, but not both.
        if cmd and args:
            deploy_body['args'] = args
        elif cmd:
            deploy_body['cmd'] = cmd
        else:
            deploy_body['args'] = args

        return deploy_body

    def deploy(self):
        endpoint = self.config.get('marathon_endpoint', '')
        container_name = self.config.get('container_name', '')
        path_id = self.config.get('marathon_id', '')

        yn = moves.input("Are you sure, you want to deploy '{}' to Marathon (y/n) ? ".format(container_name))
        yn = yn.lower()
        if yn not in ['yes', 'y']:
            return False

        print("Creating deploy request for '{}'".format(container_name))
        deploy_body = self.create_deploy_body()
        print(json.dumps(deploy_body, indent=4))

        print("Deploying '{}'..".format(path_id))
        resp = requests.post(endpoint + '/apps', data=json.dumps(deploy_body),
                             headers={'Content-Type': 'application/json'})
        if resp.status_code == 201:
            resp_json = resp.json()
            deployments = resp_json.get('deployments')
            print("Deployed '{}' successfully.".format(deployments[0]["id"]))
        else:
            print('Failed to deploy')
        print(json.dumps(resp.json(), indent=4))
