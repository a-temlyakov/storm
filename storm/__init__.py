# -*- coding: utf-8 -*-

from __future__ import print_function

from .ssh_config import ConfigParser
from .exceptions import StormValueError

from operator import itemgetter

import getpass

__version__ = '0.6.3'


class Storm(object):

    def __init__(self, ssh_config_file=None):
        self.ssh_config = ConfigParser(ssh_config_file)
        self.ssh_config.load()

    def add_entry(self, name, host, user, port, id_file, custom_options=[]):
        if self.is_host_in(name):
            raise StormValueError('{0} is already in your sshconfig. use storm edit command to modify.'.format(name))

        options = self.get_options(host, user, port, id_file, custom_options)

        self.ssh_config.add_host(name, options)
        self.ssh_config.write_to_ssh_config()

        return True

    def edit_entry(self, name, host, user, port, id_file, custom_options=[]):
        if not self.is_host_in(name):
            raise StormValueError('{0} doesn\'t exists in your sshconfig. use storm add command to add.'.format(name))

        options = self.get_options(host, user, port, id_file, custom_options)

        self.ssh_config.update_host(name, options)
        self.ssh_config.write_to_ssh_config()

        return True

    def update_entry(self, name, **kwargs):
        if not self.is_host_in(name, regexp_match=True):
            raise StormValueError('{0} doesn\'t exists in your sshconfig. use storm add command to add.'.format(name))

        self.ssh_config.update_host(name, kwargs)
        self.ssh_config.write_to_ssh_config()

        return True

    def delete_entry(self, name):
        self.ssh_config.delete_host(name)
        self.ssh_config.write_to_ssh_config()

        return True

    def list_entries(self, order=False, only_servers=False):

        config_data = self.ssh_config.config_data

        # required for the web api.
        if only_servers:
            new_config_data = []
            for index, value in enumerate(config_data):
                if value.get("type") == 'entry' and value.get("host") != '*':
                    new_config_data.append(value)

            config_data = new_config_data

        if order:
            config_data = sorted(config_data, key=itemgetter("host"))
        return config_data

    def delete_all_entries(self):
        self.ssh_config.delete_all_hosts()

        return True

    def search_host(self, search_string):
        results = self.ssh_config.search_host(search_string)
        formatted_results = []
        for host_entry in results:
            formatted_results.append("    {0} -> {1}@{2}:{3}\n".format(
                host_entry.get("host"),
                host_entry.get("options").get("user", getpass.getuser()),
                host_entry.get("options").get("hostname"),
                host_entry.get("options").get("port", 22),
            ))

        return formatted_results

    def get_options(self, host, user, port, id_file, custom_options):
        options = {
            'hostname': host,
            'user': user,
            'port': port,
        }

        if id_file:
            options.update({
                'identityfile': id_file,
            })

        if len(custom_options) > 0:
            for custom_option in custom_options:
                if '=' in custom_option:
                    key, value = custom_option.split("=")

                    options.update({
                        key: value,
                    })

        return options

    def is_host_in(self, host, regexp_match=False):
        import re
        for host_ in self.ssh_config.config_data:
            if host_.get("host") == host or (regexp_match and re.match(host, host_.get("host"))):
                return True
        return False
