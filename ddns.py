#! /usr/bin/env python3
import time
import logging
import yaml

import local_ip
import dnsserver


def get_config(filename='./config.yaml'):
    with open(filename) as f:
        return yaml.load(f)


def work(dns_manager: dnsserver.DNSServer, cnf: dict):
    ip = local_ip.get_local_ip()
    logging.info(ip)
    dns_manager.clear()
    logging.debug(cnf.get('dnsrecord', []))
    dns_manager.add_dns_record(cnf.get('dnsrecord', []))
    dns_manager.update_address(ip)


if __name__ == '__main__':
    cnf = get_config()
    log_cnf = cnf.get('log', {})
    log_level = logging.getLevelName(str.upper(log_cnf.get('level', '')))
    logging.basicConfig(
        level=log_level,
        format=log_cnf.get('fmt', ''),
    )
    dnsserver_cnf = cnf.get('dnsserver', {})
    dnsserver_name = dnsserver_cnf['name']
    dns_manager = dnsserver.servers[dnsserver_name](dnsserver_cnf)
    while True:
        cnf = get_config()
        work(dns_manager, cnf)
        time.sleep(60 * 15)
