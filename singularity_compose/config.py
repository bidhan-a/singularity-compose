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

    def __init__(self, config_file, service_name, override_file=None, force_pull=None):
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
                            mapping['containerPortType'] = 'LITERAL'
                            mapping['hostPortType'] = 'FROM_OFFER'
                            port_mappings.append(mapping)
                            port_index += 1
        self._data["portMappings"] = port_mappings

        # Extract data from labels
        labels = self._data.get('labels', None)
        if labels:
            # Singularity data
            self._data["singularity_email"] = labels.get('mesos.singularity.admin_email', '')
            self._data["singularity_endpoint"] = labels.get('mesos.singularity.endpoint', '')

            # Host attributes
            self._data["host_attributes"] = combine_props_to_dict(labels, 'mesos.singularity.host.attributes')

            # Slave placement
            self._data['slave_placement'] = labels.get('mesos.singularity.slave.placement', '')

            # Cron schedule
            self._data['cron_schedule'] = labels.get('mesos.singularity.cron.schedule', '')

            # Resources
            self._data['cpus'] = float(labels.get('mesos.singularity.resources.cpus', '0'))
            self._data['memory'] = float(labels.get('mesos.singularity.resources.memory', '0'))
            self._data['disk'] = float(labels.get('mesos.singularity.resources.disk', '0'))
            self._data['num_ports'] = int(labels.get('mesos.singularity.resources.numports', '0'))

            # Docker
            if force_pull and force_pull in ['true', 'false']:
                forcepull = force_pull
            else:
                forcepull = labels.get('mesos.singularity.docker.forcepull', 'false')
            self._data['force_pull_image'] = True if forcepull == 'true' else False

            self._data['docker_params'] = combine_props_to_dict(labels, 'mesos.singularity.docker.params')

        # Arguments
        build = self._data.get('build', None)
        if build:
            self._data['arguments'] = build.get('args', [])

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
