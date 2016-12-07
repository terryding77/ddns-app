#! /usr/bin/env python3
import time
import requests
import alidns

def get_local_ip():
    try:
        ip = requests.get('http://ipinfo.io/json').json()['ip']
    except Exception as e:
        print(e)
        print('[MESSAGE] retry in 10 seconds')
        time.sleep(10)
        return get_local_ip()
    return ip

def work():
    local_ip = get_local_ip()
    alidns.refresh_cnf()
    for domain_name, registered_ip, prefix, record_id in alidns.get_dns_list():
        if local_ip != registered_ip:
            alidns.update_dns(domain_name, local_ip, prefix, record_id)

if __name__ == '__main__':
    while True:
        work()
        time.sleep(60 * 15)
