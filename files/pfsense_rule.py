#!/usr/bin/env python
# -*- coding: utf-8 -*-

DOCUMENTATION = '''
module: pfsense_rule
Owner : Raghunanandan Ramesha
short_description: Manages pf rules of pFsense
description:
  - Manages pf rules of pFsense.
version_added: "0.0.1"
options:
  name:
    description:
      - Name used to identify the rule
    required: true

'''

EXAMPLES = '''
    - name: Set rule
      pfsense_rule:
        name: IP_rule

    - name: Delete rule
      pfsense_rule:
        name: IP_rule
        action: remove
'''

from ansible.module_utils.basic import *
import datetime


def _add_rule(action, disabled, interface, tcpipversion, protocol, source,
              sourceport, destination, destinationport, log, description):
    script='''
require_once("config.inc");
require_once("functions.inc");
require_once("filter.inc");
require_once("shaper.inc");
require_once("ipsec.inc");
require_once("vpn.inc");

/* invalidate interface cache */
get_interface_arr(true);

$retval = 0;
$retval = filter_configure();

clear_subsystem_dirty('filter');

pfSense_handle_custom_code("/usr/local/pkg/firewall_rules/apply");

echo "The settings have been applied. The firewall rules are now reloading in the background.<br/>";

filter_configure_sync();
'''
    return 0, '', ''


def _remove_rule():
    return 0, '', ''


def main():
    module = AnsibleModule(
        argument_spec=dict(
            action=dict(required=False, default='pass', choices=['pass', 'block', 'reject']),
            disabled=dict(required=False, default='pass', choices=['true', 'false']),
            interface=dict(required=True),
            tcpipversion=dict(required=False, default='ipv4', choices=['ipv4', 'ipv6', 'ipv4+ipv6']),
            protocol=dict(required=False, default='tcp', choices=['tcp',
                                                                  'udp',
                                                                  'tcpudp',
                                                                  'icmp',
                                                                  'esp',
                                                                  'ah',
                                                                  'gre',
                                                                  'ipv6',
                                                                  'igmp',
                                                                  'ospf',
                                                                  'any',
                                                                  'carp',
                                                                  'pfsync']),
            source=dict(required=False, default='any'),
            sourceport=dict(required=False, default='any'),
            destination=dict(required=False, default='any'),
            destinationport=dict(required=False, default='any'),
            log=dict(required=False, default='false'),
            description=dict(required=False, default=''),
            state=dict(required=False, default='add', choices=['present', 'absent'])
        ),
        supports_check_mode=True,
        mutually_exclusive=[],
        required_one_of=[['type']]
    )
    startd = datetime.datetime.now()

    params = module.params

    if params['state'] == 'present':
        rc, out, err = _add_rule(action=params['action'],
                                 disabled=params['disabled'],
                                 interface=params['interface'],
                                 tcpipversion=params['tcpipversion'],
                                 protocol=params['protocol'],
                                 source=params['source'],
                                 sourceport=params['sourceport'],
                                 destination=params['destination'],
                                 destinationport=params['destinationport'],
                                 log=params['log'],
                                 description=params['description'])
        endd = datetime.datetime.now()
        delta = endd - startd
        module.exit_json(
            cmd="remove_alias",
            stdout=out.rstrip("\r\n"),
            stderr=err.rstrip("\r\n"),
            rc=rc,
            start=str(startd),
            end=str(endd),
            delta=str(delta),
            changed=True
        )
    elif params['state'] == 'absent':
        rc, out, err = _remove_rule()
        endd = datetime.datetime.now()
        delta = endd - startd
        module.exit_json(
            cmd="remove_alias",
            stdout=out.rstrip("\r\n"),
            stderr=err.rstrip("\r\n"),
            rc=rc,
            start=str(startd),
            end=str(endd),
            delta=str(delta),
            changed=True
        )
    else:
        module.fail_json(msg='Incorrect state value, possible choices: absent, present(default)')


######################################################################
main()