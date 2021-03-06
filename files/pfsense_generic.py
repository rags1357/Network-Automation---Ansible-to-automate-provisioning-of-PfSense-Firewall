#!/usr/bin/env python
# -*- coding: utf-8 -*-

DOCUMENTATION = '''
---
module: pfsense_generic
Owner : Raghunandan Ramesha
short_description: Manages Generic options of a pfsense box
description:
  - Manages Generic options of pFsense (such as hostname, domain or dns global servers).
version_added: "0.0.1"
options:
  option:
    description:
      - Option to set in general options. Could be 'dns', 'hostname', 'domain', 'ntptimeserver', 'timezone'
    required: true
  value:
    description:
      - The value of the option. In the case of dns, hostname and timezone must be a string, but for domain and
      ntptimeserver has to be a list of strings.
    required: false
'''

EXAMPLES = '''
# Set pFsense hostname
- pfsense_generic: option=hostname value=firewall1

# Set pFsense DNS servers
- name: Set DNS servers
  pfsense_generic:
    option: dns
      value:
        - 192.168.1.1
        - 8.8.4.4
'''

from ansible.module_utils.basic import *
import datetime


def _write_config(module, path, value):
    pfsh_command = "/usr/local/sbin/pfSsh.php"

    script = """
require_once("config.inc");
require_once("functions.inc");
require_once("filter.inc");
require_once("shaper.inc");
get_interface_arr(true);
global $config;
$config = parse_config(true);
{path} = {value};
unlink_if_exists("/tmp/config.cache");
write_config();
unlink_if_exists("/tmp/config.cache");
filter_configure();
exec
exit
"""

    startd = datetime.datetime.now()

    rc, out, err = module.run_command([pfsh_command],
                                      executable=pfsh_command,
                                      data=script.format(path=path, value=value),
                                      use_unsafe_shell=False)
    endd = datetime.datetime.now()
    delta = endd - startd
    if out is None:
        out = ''
    if err is None:
        err = ''
    module.exit_json(
        cmd=pfsh_command,
        stdout=out.rstrip("\r\n"),
        stderr=err.rstrip("\r\n"),
        rc=rc,
        start=str(startd),
        end=str(endd),
        delta=str(delta),
        changed=True
    )


def hostname(module, host_name):
    if type(host_name) is not str:
        module.fail_json(msg='Value for HostName is not a string')

    php_option = "$config['system']['hostname']"
    php_value = "'"+host_name+"'"
    _write_config(module, php_option, php_value)


def domain(module, domain_name):
    if type(domain_name) is not str:
        module.fail_json(msg='Value for Domain Name is not a string')
    php_option = "$config['system']['domain']"
    php_value = "'"+domain_name+"'"
    _write_config(module, php_option, php_value)


def dns(module, server_list):
    if type(server_list) is not list:
        module.fail_json(msg='Value for dns is not a list')

    php_option = "$config['system']['dnsserver']"
    php_value = "array('"+"','".join(server_list)+"')"
    _write_config(module, php_option, php_value)


def ntptimeserver(module, server_list):
    if type(server_list) is not list:
        module.fail_json(msg='Value for NTP server is not a list')

    php_option = "$config['system']['timeservers']"
    php_value = "'" + " ".join(server_list) + "'"
    _write_config(module, php_option, php_value)


def timezone(module, time_zone):
    if type(time_zone) is not str:
        module.fail_json(msg='Value for TimeZone is not a string')

    php_option = "$config['system']['timezone']"
    php_value = "'" + time_zone + "'"
    _write_config(module, php_option, php_value)


def main():
    module = AnsibleModule(
        argument_spec=dict(
            option=dict(required=True, choices=['dns',
                                                'hostname',
                                                'domain',
                                                'ntptimeserver',
                                                'timezone']),
            value=dict(required=True, default=None)
        ),
        supports_check_mode=True,
        mutually_exclusive=[],
        required_one_of=[['option']]
    )

    params = module.params

    if params['option'] == 'dns' and type(params['value']) is list:
        dns(module, params['value'])
    elif params['option'] == 'ntptimeserver' and type(params['value']) is list:
        ntptimeserver(module, params['value'])
    elif params['option'] == 'timezone' and type(params['value']) is str:
        timezone(module, params['value'])
    elif params['option'] == 'hostname' and type(params['value']) is str:
        hostname(module, params['value'])
    elif params['option'] == 'domain' and type(params['value']) is str:
        domain(module, params['value'])
    else:
        module.fail_json(msg='Incorrect params ' + str(type(params['option'])) + str(params['value']))


# TODO: Check that the environment is a pfsense at module start

######################################################################
main()