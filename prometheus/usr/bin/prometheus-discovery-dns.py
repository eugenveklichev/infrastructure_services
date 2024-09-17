#!/usr/bin/env python3

__author__ = "Boris Suhinin"
__email__  = "boris.sukhinin@corp.mail.ru"

import sys
import os
import re
import socket
import json
import logging


def read_config_lines(config_path):
    if not os.path.isfile(config_path):
        logging.error('Config file "%s" does not exist. Aborting...', config_path)
        sys.exit(1)
    logging.info('Reading service definitions: %s', config_path)
    with open(config_path, 'r') as fp:
        lines = [line.strip() for line in fp.readlines()]
    return lines


def process_config_entry(config_entry):
    discovered = []
    split = config_entry.split()

    # service_fqdn:port/path/to/metrics
    # e.g. my.service.local.odkl.ru:8080/metrics
    match = re.match(r'^([^:]+)(:\d+)(/[^\s]*)$', split[0])
    if match is None:
        raise ValueError('Service definition is invalid')
    service, port, path = match.groups('')

    # Parse label KV-pairs.
    common_labels = {'__metrics_path__': path}
    for kv in split[1:]:
        key, value = kv.split('=', 1)
        common_labels[key] = value

    # Resolve service FQDN to multiple addresses and then resolve
    # each address back to (hopefully different) individual FQDNs.
    _, _, ips = socket.gethostbyname_ex(service)
    for ip in sorted(ips):
        fqdn, _, _ = socket.gethostbyaddr(ip)
        labels = extract_labels_from_fqdn(fqdn)
        labels.update(common_labels)
        discovered.append({'targets': [fqdn + port], 'labels': labels})

    logging.info('Discovered %d targets for %s', len(discovered), service)
    return discovered


def extract_labels_from_fqdn(fqdn):
    match = re.match(r'^(\d+)\.([a-zA-Z0-9_-]+)\.([a-zA-Z0-9_-]+)\.([a-zA-Z0-9_-]+)\.(odkl|idzn)\.ru$', fqdn)
    if match is None:
        return {'host': fqdn}
    (no, application, queue, datacenter, namespace) = match.groups()
    return {'application': '%s.%s' % (application, queue),
            'datacenter': datacenter,
            'instance': '%s.%s.%s' % (no, application, queue),
            'namespace': namespace}


def write_discovery_results(discovered, output_path):
    logging.info('Writing discovery results: %s', output_path)
    output = json.dumps(discovered, sort_keys=True, indent=2, separators=(',', ': ')) + '\n'
    with open(output_path, 'w') as fp:
        fp.write(output)


def main():
    logging.basicConfig(format='%(levelname)s %(message)s', level=logging.INFO)

    discovered = []
    config_lines = read_config_lines(sys.argv[1])
    for line_number, dns_entry in enumerate(config_lines):
        if dns_entry and not dns_entry.startswith('#'):
            try:
                discovered += process_config_entry(dns_entry)
            except Exception as e:
                logging.error('Error while processing line %d: %s', line_number + 1, e)
    write_discovery_results(discovered, sys.argv[2])


if __name__ == '__main__':
    main()