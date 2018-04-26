import json


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

        deploy_body = {
            "id": self.config['container_name'],
            "args": self.config.get('arguments', []),
            "cmd": self.config.get('entrypoint', None),
            "container": {
                "type": "DOCKER",
                "volumes": self.config.get('volumes', []),
                "docker": {
                    "image": self.config["image"],
                    "privileged": self.config.get("privileged", False),
                    "forcePullImage": self.config.get("force_pull_image", False),
                    "parameters": parameters
                },
                "portMappings": self.config.get("portMappings", [])
            },
            "cpus": self.config.get('cpus', ''),
            "mem": self.config.get('memory', ''),
            "disk": self.config.get('disk', ''),
            "requirePorts": True,
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
        return deploy_body

    def deploy(self):
        print(json.dumps(self.create_deploy_body(), indent=4))
