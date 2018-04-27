import re
import yaml
import pprint


def merge_dicts(source, destination):
    for key, value in source.items():
        if isinstance(value, dict):
            node = destination.setdefault(key, {})
            merge_dicts(value, node)
        else:
            destination[key] = value

    return destination


def combine_props_to_dict(parent_dict, pattern):
    res = {}
    for key in parent_dict:
        match = re.search('^{0}.(.+)?'.format(pattern), key)
        if match:
            res[match.group(1)] = parent_dict[key]
    return res


class Config(object):

    def __init__(self, config_file, service_name, platform, override_file=None, force_pull=None):
        self._data = None

        with open(config_file) as config:
            config_obj = yaml.load(config)
            if override_file:
                with open(override_file) as override:
                    override_obj = yaml.load(override)
                    config_obj = merge_dicts(override_obj, config_obj)

            # Get service by service_name
            services = config_obj.get('services', None)
            if services:
                self._data = services.get(service_name, None)

        if not self._data:
            raise Exception("Service '{}' is not defined".format(service_name))

        # Volumes
        vols = self._data.get('volumes', [])
        volumes = []
        if vols:
            for vol in vols:
                items = vol.split(":")
                volumes.append({'hostPath': items[0], 'containerPath': items[1], 'mode': 'RW'})
            self._data["volumes"] = volumes

        # Ports (Add if network_mode is not "host")
        port_mappings = []
        network_mode = self._data.get('network_mode', None)
        if network_mode and network_mode != 'host':
            ports = self._data.get('ports', [])
            port_index = 0
            if ports:
                for port in ports:
                    matches = re.search('(\d+):(\d+)/?(tcp|udp)?', port)
                    mapping = {}
                    if matches:
                        mapping['hostPort'] = int(matches.group(1))
                        mapping['containerPort'] = int(matches.group(2))
                        mapping['protocol'] = matches.group(3) if matches.group(3) else 'tcp'
                        port_mappings.append(mapping)
                    else:
                        # dynamic port mapping
                        matches = re.search('(\d+)/?(tcp|udp)?', port)

                        if matches:
                            mapping['hostPort'] = port_index
                            mapping['containerPort'] = int(matches.group(1))
                            mapping['protocol'] = matches.group(2) if matches.group(2) else 'tcp'
                            if platform == 'singularity':
                                mapping['containerPortType'] = 'LITERAL'
                                mapping['hostPortType'] = 'FROM_OFFER'
                            elif platform == 'marathon':
                                mapping['name'] = "default"
                            port_mappings.append(mapping)
                            port_index += 1
        self._data["port_mappings"] = port_mappings

        # Placement constraints
        host_attributes = {}
        try:
            constraints = self._data['deploy']['placement']['constraints']
            for c in constraints:
                kv = c.split('==')
                host_attributes[kv[0].strip()] = kv[1].strip()
        except KeyError:
            pass
        self._data["host_attributes"] = host_attributes

        # Extract data from extension field (previously labels were used)
        x_compose_paas = config_obj.get('x-compose-paas', None)
        if x_compose_paas:
            # Singularity
            singularity_data = x_compose_paas.get('singularity', None)
            if singularity_data:
                self._data["singularity_email"] = singularity_data.get('admin_email', '')
                self._data["singularity_endpoint"] = singularity_data.get('endpoint', '')
                # Slave placement
                self._data['slave_placement'] = singularity_data.get('slave_placement', '')
                # Cron schedule
                self._data['cron_schedule'] = singularity_data.get('cron_schedule', '')

            # Marathon
            marathon_data = x_compose_paas.get('marathon', None)
            if marathon_data:
                self._data['marathon_fetch'] = marathon_data.get('fetch', {})
                self._data['marathon_resource_roles'] = marathon_data.get('resource_roles', ['*'])
                self._data['marathon_id'] = marathon_data.get('id', '')
                self._data['marathon_endpoint'] = marathon_data.get('endpoint', '')

            # Resources
            resources_data = x_compose_paas.get('resources', None)
            if resources_data:
                self._data['cpus'] = float(resources_data.get('cpus', '0'))
                self._data['memory'] = float(resources_data.get('memory', '0'))
                self._data['disk'] = float(resources_data.get('disk', '0'))
                self._data['num_ports'] = int(resources_data.get('numports', '0'))

            # Docker
            docker_data = x_compose_paas.get('docker', None)
            if docker_data:
                if force_pull and force_pull in ['true', 'false']:
                    forcepull = force_pull
                else:
                    forcepull = docker_data.get('forcepull', 'false')

                self._data['force_pull_image'] = True if forcepull == 'true' else False
                self._data['docker_params'] = docker_data.get('params', {})

        # Arguments (split `command`)
        command = self._data.get('command', None)
        if command:
            self._data['arguments'] = command.split(' ')

    def __getitem__(self, key):
        if key not in self._data:
            print("Warning: {} not defined in config".format(key))
        return self._data.get(key, None)

    def __getattr__(self, key):
        return self.__getitem__(key)

    def __str__(self):
        return pprint.pformat(self._data, indent=4, depth=2)

    def get(self, key, default=None):
        return self._data.get(key, default)
