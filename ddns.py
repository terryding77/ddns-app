#! /usr/bin/env python3
import time
import requests
def get_local_ip():
    try:
        ip = requests.get('http://ipinfo.io/json').json()['ip']
    except Exception as e:
        print(e)
        print('[MESSAGE] retry in 10 seconds')
        time.sleep(10)
        return get_local_ip()
    return ip

def get_alidns_ip():
    pass

def set_alidns_ip():
    pass

def work():
    local_ip = get_local_ip()
    print(local_ip)
    registered_ip = get_alidns_ip()
    if local_ip != registered_ip:
        set_alidns_ip()

if __name__ == '__main__':
    while True:
        work()
        time.sleep(60 * 15)
